import pandas as pd 

def show_commands(user):
    """
    Bot S.A.B manual
    """
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello <@%s> :wave: ! I'm so glad that you are here.\nS.A.B can help you many things within Slack." % user
                }
            }],
        "attachments": [
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":paw_prints: *Commands* :paw_prints:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "`news [category], [country], [language], [query]`. Returns articles in that chosen channel.\n\n"
                                "Read this to command properly: `[https://newsapi.org/docs/endpoints/sources]`\n\n"
                                # "Possible `[category]` options: `[business] [entertainment] [general] [health] [science] [sports] [technology]`\n\n"
                                # "The 2-letter ISO 3166-1 code (lowercase) for the `[country]`\n\n"
                                # "The 2-letter ISO-639-1 code of the `[language]`\n\n"
                                # "*Optional!* The query to use. Advanced search for the specific keyword `[query]`"
                                "`covid [country 1], [country 2], ... [country n]`. Return covid situation in each country.\n\n"
                                "Read this to command properly: `[https://api.covid19api.com/countries]`"
                            )
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":paw_prints: *Examples* :paw_prints:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "`news science, us, en, space`\n\n"
                                "`covid vietnam, united-states, japan`"
                            )
                        }
                    }
                ]
            }
        ]
    }

def tableize(df):
    """
    Pretty print dataframe
    """
    if not isinstance(df, pd.DataFrame):
        return
    df_columns = df.columns.tolist() 
    max_len_in_lst = lambda lst: len(sorted(lst, reverse=True, key=len)[0])
    align_center = lambda st, sz: "{0}{1}{0}".format(" "*(1+(sz-len(st))//2), st)[:sz] if len(st) < sz else st
    align_right = lambda st, sz: "{0}{1} ".format(" "*(sz-len(st)-1), st) if len(st) < sz else st
    max_col_len = max_len_in_lst(df_columns)
    max_val_len_for_col = dict([(col, max_len_in_lst(df.iloc[:,idx].astype('str'))) for idx, col in enumerate(df_columns)])
    col_sizes = dict([(col, 2 + max(max_val_len_for_col.get(col, 0), max_col_len)) for col in df_columns])
    build_hline = lambda row: '+'.join(['-' * col_sizes[col] for col in row]).join(['+', '+'])
    build_data = lambda row, align: "|".join([align(str(val), col_sizes[df_columns[idx]]) for idx, val in enumerate(row)]).join(['|', '|'])
    hline = build_hline(df_columns)
    out = [hline, build_data(df_columns, align_center), hline]
    for _, row in df.iterrows():
        out.append(build_data(row.tolist(), align_right))
    out.append(hline)
    return "\n".join(out)