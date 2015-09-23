def differences(dataframe, guiding_funcs):
    basic_e1 = dataframe[dataframe.optimiser_guiding_function == 'e1']
    basic_others = {gf: dataframe[dataframe.optimiser_guiding_function == gf]
                    for gf in guiding_funcs}

    basic_e1.sort(columns=['Ne', 'training_set_number'], inplace=True)
    basic_e1.reset_index(inplace=True, drop=True)
    for df in basic_others:
        df.sort(columns=['Ne', 'training_set_number'], inplace=True)
        df.reset_index(inplace=True, drop=True)

    for gf, df in basic_others.items():
        print(gf, (basic_e1.test_error_simple - df.test_error_simple).mean())