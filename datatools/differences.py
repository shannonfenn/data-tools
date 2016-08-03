def differences(dataframe, guiding_funcs):
    baseline = dataframe[dataframe.guiding_function == 'e1']
    basic_others = {gf: dataframe[dataframe.guiding_function == gf]
                    for gf in guiding_funcs}

    baseline.sort(columns=['Ne', 'trg_set_num'], inplace=True)
    baseline.reset_index(inplace=True, drop=True)
    for df in basic_others:
        df.sort(columns=['Ne', 'trg_set_num'], inplace=True)
        df.reset_index(inplace=True, drop=True)

    for gf, df in basic_others.items():
        print(gf, (baseline.test_error - df.test_error).mean())
