
from imports import *

class TabGenerator:
    def __init__(self, first_data, question_var, question_text, base_text, display_structure,
                 table_number, study_name, client_name, month, year, question_type, mean_var,
                 filter_condition=None, show_sigma=True):
        self.df = first_data.copy()
        self.question_var = question_var
        self.question_text = question_text
        self.base_text = base_text
        self.display_structure = display_structure
        self.codes_dict = {payload: label for row_type, label, payload in (display_structure or [])
                           if row_type == "code"}
        self.multi_vars = [payload for row_type, label, payload in (display_structure or [])
                           if row_type == "code" and isinstance(payload, str)]
        self.table_number = table_number
        self.study_name = study_name
        self.client_name = client_name
        self.month = month
        self.year = year
        self.question_type = question_type
        self.mean = mean_var
        self.filter_condition = filter_condition
        self.show_sigma = show_sigma

    def _get_multi_columns(self):
        if self.multi_vars:
            return self.multi_vars
        return [k for k in self.codes_dict.keys() if isinstance(k, str)]
    def _stats_from_distribution(self, counts, factors, base_n):
        """
        Compute stats (Mean, Std.dev, Std.err, Median) from a discrete distribution:
        - counts: dict {code -> frequency}
        - factors: dict {code OR label -> numeric score}
        Allows factor lookup by code or by the display label for that code.
        """
        xs, ws = [], []
        for code, cnt in counts.items():
            if cnt <= 0:
                continue
            if code in factors:
                val = factors[code]
            else:
                # try label text if provided in display_structure
                label = self.codes_dict.get(code)
                if label in factors:
                    val = factors[label]
                else:
                    # no factor -> skip this code
                    continue
            xs.append(float(val))
            ws.append(int(cnt))

        if not xs or sum(ws) == 0:
            return {}

        x = np.array(xs, dtype=float)
        w = np.array(ws, dtype=float)

        mean = (w * x).sum() / w.sum()

        # Weighted sample std.dev (frequency weights, unbiased)
        if w.sum() > 1:
            var_num = (w * (x - mean) ** 2).sum()
            var_den = w.sum() - 1
            std_val = float(np.sqrt(var_num / var_den))
            sem_val = float(std_val / np.sqrt(w.sum()))
        else:
            std_val = 0.0
            sem_val = 0.0

        # Weighted median
        cum = np.cumsum(w / w.sum())
        median_val = float(x[np.searchsorted(cum, 0.5)])

        return {
            "Mean":    [f"{mean:.2f}", ""],
            "Std.dev": [f"{std_val:.2f}", ""],
            "Std.err": [f"{sem_val:.2f}", ""]            
        }
    
    def calculate_sigma_and_no_answer(self, df_filtered, base_n, total_count, question_type):
        result = {}
        if base_n == 0:
            no_answer_count = 0
        elif question_type == "single":
            no_answer_count = max(0, base_n - int(total_count))
        elif question_type == "multi":
            multi_cols = self._get_multi_columns()
            if not multi_cols:
                answered_mask = df_filtered.notna().any(axis=1)
            else:
                answered_mask = (df_filtered[multi_cols] == 1).any(axis=1)
            no_answer_count = int(base_n - int(answered_mask.sum()))

        else:
            no_answer_count = 0

        no_answer_percent = (no_answer_count / base_n) * 100 if base_n > 0 else 0
        if no_answer_count > 0:
            result["No Answer"] = [no_answer_count, f"{no_answer_percent:.2f}%"]

        sigma_count = total_count + no_answer_count
        sigma_percent = (sigma_count / base_n) * 100 if base_n > 0 else 0
        result["Sigma"] = [sigma_count, f"{sigma_percent:.2f}%"]
        return result
    
    def calculate_stats(self, df_filtered):
        """
        Flexible stats:
        - If self.mean is a string -> use that numeric df column
        - If self.mean is a dict   -> treat as factor scores for SINGLE-response rating codes
                                      (keys can be codes OR labels from display_structure)
        """
        base_n = len(df_filtered)
        if not self.mean or base_n == 0:
            return {}

        # Case 1: numeric column
        if isinstance(self.mean, str):
            col = self.mean
            if col in df_filtered.columns:
                s = pd.to_numeric(df_filtered[col], errors="coerce").dropna()
                if s.empty:
                    return {}
                mean = s.mean()
                std_val = s.std(ddof=1)
                sem_val = s.sem(ddof=1)
                median_val = s.median()
                return {
                    "Mean":    [f"{mean:.2f}", ""],
                    "Std.dev": [f"{std_val:.2f}", ""],
                    "Std.err": [f"{sem_val:.2f}", ""],
                    "Median":  [f"{median_val:.2f}", ""],
                }
            return {}

        # Case 2: factors dict for single-response rating scale
        if isinstance(self.mean, dict):
            if self.question_type != "single":
                # factor-based mean applies to single-response rating questions
                return {}
            # distribution of the single-response variable
            series = df_filtered[self.question_var]
            counts = series.value_counts(dropna=True).to_dict()
            return self._stats_from_distribution(counts, self.mean, base_n) or {}

        # Unsupported type
        return {}

    def generate_crosstab(self, banner_segments, display_structure=None):
        if display_structure is None:
            display_structure = self.display_structure

        banner_data = {}
        base_ns = {}
        labels = [label for _, label, _ in display_structure]
        used_labels = set(labels)

        for banner in banner_segments:
            condition = banner.get("condition")
            banner_id = banner["id"]

            if self.filter_condition:
                df_base_filter = self.df.query(self.filter_condition)
            else:
                df_base_filter = self.df

            if condition:
                df_filtered = df_base_filter.query(condition)
            else:
                df_filtered = df_base_filter

            base_n = len(df_filtered)
            base_ns[banner_id] = base_n
            banner_data[banner_id] = {}
            total_count = 0

            for row_type, label_text, payload in display_structure:
                if self.question_type == "single":
                    if row_type == "code":
                        code = payload
                        count = int((df_filtered[self.question_var] == code).sum())
                        pct = (count / base_n * 100) if base_n > 0 else 0
                        banner_data[banner_id][label_text] = [count, f"{pct:.2f}%"]
                        total_count += count
                    elif row_type == "net" and isinstance(payload, list):
                        count = int(df_filtered[self.question_var].isin(payload).sum())
                        pct = (count / base_n * 100) if base_n > 0 else 0
                        banner_data[banner_id][label_text] = [count, f"{pct:.2f}%"]
                        used_labels.add(label_text)

                elif self.question_type == "multi":
                    if row_type == "code":
                        col = payload
                        count = int((df_filtered[col] == 1).sum()) if col in df_filtered.columns else 0
                        pct = (count / base_n * 100) if base_n > 0 else 0
                        banner_data[banner_id][label_text] = [count, f"{pct:.2f}%"]
                        total_count += count
                    elif row_type == "net" and isinstance(payload, list):
                        present = [c for c in payload if c in df_filtered.columns]
                        if present:
                        # ✅ Count respondents who selected ANY of the listed stubs (row-wise OR)
                            mask_any = (df_filtered[present] == 1).any(axis=1)
                            count = int(mask_any.sum())
                        else:
                            count = 0
                        pct = (count / base_n * 100) if base_n > 0 else 0
                        banner_data[banner_id][label_text] = [count, f"{pct:.2f}%"]
                        used_labels.add(label_text)


            if self.show_sigma:
                sigma_data = self.calculate_sigma_and_no_answer(df_filtered, base_n, total_count, self.question_type)
                for lbl, vals in sigma_data.items():
                    banner_data[banner_id][lbl] = vals
                    used_labels.add(lbl)
            stats_data = self.calculate_stats(df_filtered)
            for lbl, vals in stats_data.items():
                banner_data[banner_id][lbl] = vals
                used_labels.add(lbl)

        final_labels = [label for _, label, _ in display_structure]
        if self.show_sigma and "No Answer" in used_labels:
            final_labels.append("No Answer")
        if self.show_sigma and "Sigma" in used_labels:
            final_labels.append("Sigma")
        for stat in ["Mean", "Std.err", "Std.dev", "Median"]:
            if stat in used_labels:
                final_labels.append(stat)

        header = ["Label"] + [f"{seg['id']} ({seg['label']})" for seg in banner_segments]
        output = [["Base"] + [base_ns[seg["id"]] for seg in banner_segments]]

        for label in final_labels:
            count_row = [label]
            percent_row = [""]
            has_percent = False
            for seg in banner_segments:
                values = banner_data[seg["id"]].get(label, [0, ""])
                count_row.append(values[0])
                percent_row.append(values[1])
                if values[1]:
                    has_percent = True
            output.append(count_row)
            if has_percent:
                output.append(percent_row)

        return pd.DataFrame(output, columns=header)

    

    