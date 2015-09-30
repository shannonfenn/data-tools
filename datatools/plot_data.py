import ggplot as gg
import numpy as np
import pandas as pd
import json
import easygui


def count_generalised(df, N):
    target_names = ['test_error_target_{}'.format(i) for i in range(N)]
    count_names = ['tz{}'.format(i) for i in range(N)]
    for c in count_names:
        df[c] = False
    for c, t in zip(count_names, target_names):
        df[c] = df[t] == 0


def get_No(df):
    if min(df['No']) == max(df['No']):
        return min(df['No'])
    else:
        raise ValueError('Different values for number of outputs in results.')


def get_results():
    filename = easygui.fileopenbox(msg='Select experiment file', title='Select experiment file')
    print(filename)
    results = pd.read_json(filename)

    # results = subset(results, select = -c(final_network))

    # this is replaced by pandas categorical
    # ind <- sapply(results, is.character)
    # results[ind] <- lapply(results[ind], factor)
    # reorganise function factor

    results = results.rename(columns={'optimiser_guiding_function': 'guiding_function'})

    count_generalised(results, get_No(results))

    return results


# extract legend
# def get_legend(plot):
#     gt = gg.ggplotGrob(plot)
#     idx = grep('guide', gt.layout.name)
#     if length(idx) > 1:
#         raise ValueError('More than one match for pattern \'guide\'')
#     return gt.grobs[[idx]]


def plot_err(results, perbit, err_type, by, show_legend=True,
             colour_start=0, legend_pos=(.12, .85), legend_cols=1):

    N = get_No(results)
    legend_name = None
    scale = None
    data_frame = results

    if err_type == 'test':
        y_label = 'Test error'
    elif err_type == 'train':
        y_label = 'Training error'
    else:
        raise ValueError('unsupported value for \'err_type\'')

    if perbit:
        x_label = 'Target'

        if err_type == 'test':
            target_names = ['test_error_target_{}'.format(i) for i in range(N)]
        elif err_type == 'train':
            target_names = ['training_error_target_{}'.format(i) for i in range(N)]

        if by == 'lm' or by == 'learner>gf' or by == 'gf>learner':
            data_frame['grp'] = data_frame.learner.map(str) + ' / ' + data_frame.guiding_function
            legend_name = 'Learner / Guiding Function'
        elif by == 'learner':
            data_frame['grp'] = data_frame.learner
            legend_name = 'Learner'
        elif by == 'gf':
            data_frame['grp'] = data_frame.guiding_function
            legend_name = 'Guiding Function'
        elif by == 'tf':
            data_frame['grp'] = data_frame.transfer_functions
            legend_name = 'Transfer function'
        else:
            raise ValueError('unsupported value for \'by\'')

        # data for errors
        cols_to_keep = target_names + ['grp']
        data_frame = melt(subset(data_frame, select=cols_to_keep), id_vars='grp')
        # full per bit plot
        aesthetic = gg.aes(x='variable', y='value', color='grp')
        scale = scale_x_discrete(breaks=target_names, labels=range(1, N+1))

    else:
        # Test Error (simple) plot
        if by == 'lm':
            data_frame['grp'] = data_frame.learner + ' / ' + data_frame.guiding_function
            # aesthetic = gg.aes(x='grp', y='test_error_simple', color='grp')
            aesthetic = gg.aes(x='test_error_simple', y='grp', color='grp')
            x_label = 'Learner / Guiding Function'
            legend_name = 'Learner / Guiding Function'
        elif by == 'learner>gf':
            aesthetic = gg.aes(x='guiding_function', y='test_error_simple', color='learner')
            x_label = 'Guiding Function'
            legend_name = 'Learner'
        elif by == 'gf>learner':
            aesthetic = gg.aes(x='learner', y='test_error_simple', color='guiding_function')
            x_label = 'Learner'
            legend_name = 'Guiding Function'
        elif by == 'learner':
            aesthetic = gg.aes(x='learner', y='test_error_simple', color='learner')
            x_label = 'Learner'
        elif by == 'gf':
            aesthetic = gg.aes(x='guiding_function', y='test_error_simple', color='guiding_function')
            x_label = 'Guiding Function'
        elif by == 'tf':
            aesthetic = gg.aes(x='transfer_functions', y='test_error_simple', color='transfer_functions')
            x_label = 'Transfer function'
        else:
            raise ValueError('unsupported value for \'by\'')

    p = gg.ggplot(data_frame, aesthetic)
    p += gg.labs(x=x_label, y=y_label)
    p += gg.geom_boxplot()
    # p += gg.theme(legend_position=legend_pos)
    # p += gg.guides(color=gg.guide_legend(ncol=legend_cols, byrow=False))

    if scale:
        p += scale
    if legend_name:
        p += gg.scale_color_brewer(type='qual')
        # p += gg.scale_color_hue(h_start=colour_start, name=legend_name)

    print(p)
    return p


def plot_err_vs_target_line(results, by, func, colour_start=0, legend_pos=c(.12, .85)):
    N = get.No(results)
    if by == 'learner+gf' or by == 'lm':
        results['grp'] = results.learner + ' / ' + results.guiding_function
        legend_name = 'Learner / Guiding Function'
    elif by == 'learner':
        results['grp'] = results.learner
        legend_name = 'Learner'
    elif by == 'gf':
        results['grp'] = results.guiding_function
        legend_name = 'Guiding Function'
    else:
        raise ValueError('unsupported value for \'by\'')

    # full error per bit plot
    # data for errors
    target_names = ['test_error_target_{}'.format(i) for i in range(N)]
    cols_to_keep = target_names + ['grp']
    error_data = melt(subset(results, select=cols_to_keep), id_vars='grp')

    # change test_error_target_n   ->   n
    error_data.variable = mapvalues(error_data.variable, from=target_names, to=range(N))
    error_data.variable = as_numeric(as_character(error_data.variable))
    # apply function to aggregated data
    agg.err.dat = aggregate(value~grp+variable, error_data, func)

    p = gg.ggplot(agg.err.dat, gg.aes(x=variable, y=value, color=grp)) +\
        geom_line() +\
        gg.labs(x='Target', y='Test error') +\
        scale_color_hue(h_start=colour_start, name=legend_name) +\
        theme(legend_position=legend_pos, legend.key=element_blank())

    print(p)
    return p


def plot_gen_rate_vs_target(results, plot_type='line', colour_start=0, legend_pos=c(.12, .85)):
    N = get.No(results)
    names = ['tz{}'.format(i) for i in range(N)]
    f = paste('cbind(', paste(names, collapse=', '), ') ~', 'learner + guiding_function')
    agg = aggregate(as.formula(f), data=results, FUN=mean)
    agg = melt(agg, id=c('learner', 'guiding_function'))
    agg['grp'] = agg.learner + ' / ' + agg.guiding_function

    if plot_type == 'bar':
        p = gg.ggplot(agg, gg.aes(x=variable, y=value, fill=grp)) +\
            geom_bar(stat='identity', position=position_dodge(), colour='black')
    elif plot_type == 'line':
        p = gg.ggplot(agg, gg.aes(x=variable, y=value, colour=grp)) +\
            geom_line(gg.aes(group=grp))
    else:
        raise ValueError('unsupported value for \'plot_type\'')

    p = p + scale_x_discrete(labels=range(1, 9)) +\
        scale_fill_discrete(name='Learner / Guiding Function') +\
        gg.labs(x='Target', y='Perfect generalisation rate')
    print(p)
    return p


# def plot3_errs_gf(results, use_notch=True, show_legend=True):
#     colour_start = 0
#     N = get.No(results)
#     # depth plot
# #     cols_to_keep = c('guiding_function', paste('max_depth_target_', 0:(N-1), sep='))
# #     depth.data = melt(subset(results, select = cols_to_keep), id_vars='guiding_function')
# #     plot.depth = gg.ggplot(depth.data) + geom_boxplot(gg.aes(x=variable, y=value, color=guiding_function))

#     # data for errors
#     target_names = ['test_error_target_{}'.format(i) for i in range(N)]
#     cols_to_keep = c('guiding_function', target_names)
#     error_data = melt(subset(results, select=cols_to_keep), id_vars='guiding_function')

#     # full error per bit plot
#     plot_err_per_bit = gg.ggplot(error_data, gg.aes(x=variable, y=value, color=guiding_function)) +\
#         geom_boxplot(notch=use_notch) +\
#         gg.labs(title='Test error per target', x='target', y='error') +\
#         scale_x_discrete(breaks=target_names, range(1, N+1)) +\
#         scale_color_hue(h_start=colour_start, name='Guiding Function')

#     # Test Error (simple) plot
#     plot_test_err = gg.ggplot(results, gg.aes(x=guiding_function, y=test_error_simple, color=guiding_function)) +\
#         geom_boxplot(notch=use_notch) +\
#         gg.labs(title='Test error', x='Guiding Function', y='error') +\
#         theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) +\
#         scale_color_hue(h_start=colour_start, name='Guiding Function')

#     # training error
#     plot_training_err = gg.ggplot(results, gg.aes(x=guiding_function, y=training_error_simple, color=guiding_function)) +\
#         geom_boxplot() +\
#         gg.labs(title='Training error', x='Guiding Function', y='error') +\
#         theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) +\
#         scale_color_hue(h_start=colour_start, name='Guiding Function')

#     # get common legend
#     legend = editGrob(get_legend(plot_err_per_bit), vp=vplayout(1:2, 3))
#     # remove legends
#     plot_err_per_bit = plot_err_per_bit + theme(legend_position='none')
#     plot_test_err = plot_test_err + theme(legend_position='none')
#     plot_training_err = plot_training_err + theme(legend_position='none')
#     # generate 3 part plot with common legend
#     grid.newpage()
#     cols = if(show_legend) 3 else 2
#     pushViewport(viewport(layout=grid.layout(nrow=2, ncol=cols,
#                                              widths=unit(c(2, 2, 0.6)[1:cols], c('null', 'null')),
#                                              heights=unit(c(1.3, 1)[1:cols], c('null', 'null')))))

#     print(plot_err_per_bit, vp=vplayout(1, 1:2))
#     print(plot_test_err, vp=vplayout(2, 1))
#     print(plot_training_err, vp=vplayout(2, 2))

#     if show_legend:
#         grid.draw(legend)


def plot_errs_by_sample(results):
    p_test = gg.ggplot(gg.aes(x=num.Ne, y=test_error_simple, color=guiding_function), data=results) +\
        geom_boxplot() +\
        gg.labs(title='Test error', x='Ne', y='error')

    p_training = gg.ggplot(gg.aes(x=num.Ne, y=training_error_simple, color=guiding_function), data=results) +\
        geom_boxplot() +\
        gg.labs(title='Training error', x='Ne', y='error') +\
        theme(axis.title.y=element_blank())

    # get common legend
    legend = editGrob(get_legend(p_test), vp=vplayout(1, 3))
    # remove legends
    p_test = p_test + theme(legend_position='none')
    p_training = p_training + theme(legend_position='none')
    # generate 3 part plot with common legend
    grid.newpage()
    pushViewport(viewport(layout=grid.layout(nrow=1, ncol=3,
                                             widths=unit(c(2, 2, 0.6), c('null', 'null')),
                                             heights=unit(c(1), c('null', 'null')))))
    print(p_test, vp=vplayout(1, 1))
    print(p_training, vp=vplayout(1, 2))
    grid.draw(legend)


def plot_single_comparison(results):
    # create factor from numeric
    p_test = gg.ggplot(gg.aes(x=optimiser_name, y=test_error_simple, color=optimiser_name), data=results) +\
        geom_boxplot(notch=True) +\
        gg.labs(title='Test error', x='optimiser', y='error') +\
        scale_color_discrete(name='Optimiser')

    p_training = gg.ggplot(gg.aes(x=optimiser_name, y=training_error_simple, color=optimiser_name), data=results) +\
        geom_boxplot(notch=False) +\
        gg.labs(title='Training error', x='optimiser', y='error') +\
        theme(axis.title.y=element_blank())

    p_iterations = gg.ggplot(gg.aes(x=optimiser_name, y=total_iterations, color=optimiser_name), data=results) +\
        geom_boxplot(notch=True) +\
        gg.labs(title='Total steps', x='optimiser', y='steps')

    # get common legend
    # get common legend
    # generate 3 part plot with common legend
    grid.newpage()
    pushViewport(viewport(layout=grid.layout(nrow=2, ncol=2,
                                             widths=unit(c(2, 2), c('null', 'null')),
                                             heights=unit(c(1, 1), c('null', 'null')))))
    legend = editGrob(get_legend(p_test), vp=vplayout(2, 2))
    # remove legends
    p_test = p_test + theme(legend_position='none')
    p_training = p_training + theme(legend_position='none')
    p_iterations = p_iterations + theme(legend_position='none')

    print(p_test, vp=vplayout(1, 1))
    print(p_training, vp=vplayout(1, 2))
    print(p_iterations, vp=vplayout(2, 1))
    grid.draw(legend)


def list_lengths(x):
    if is_null(x):
        return None
    else:
        return lapply(x, length)
