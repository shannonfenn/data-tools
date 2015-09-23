library(ggplot2)
library(jsonlite)
library(reshape2)
library(tcltk)
library(grid)
library(plyr)

options(stringsAsFactors = TRUE)

ERR_TGT_INFIX <- '_err_tgt_'

get.results <- function() {
    options(stringsAsFactors = TRUE)
    jsonfile <- tk_choose.files(default = 'HMRI/', caption = 'Select experiment file', multi = FALSE,
                                filters=matrix(c('json', '.json'), 1, 2, byrow = TRUE))
    print(jsonfile)
    results <- fromJSON(jsonfile)
    results <- subset(results, select = -c(final_network))
    ind <- sapply(results, is.character) 
    results[ind] <- lapply(results[ind], factor) 
    # reorganise function factor
    results$guiding_function <- factor(
        results$optimiser_guiding_function, 
        levels = levels(results$optimiser_guiding_function)[c(1, 2, 4, 6, 8, 10, 12, 3, 5, 7, 9, 11, 13)])
    # create factor from numeric
    results$num.Ne <- factor(results$Ne)
    
    if(class(results$total_iterations) == 'list'){
        # something like the below
        for (i in 1:nrow(results)) { results$total_it[i] <- do.call(sum, results$total_iterations[i]) }
    }
    else {
        results$total_it <- results$total_iterations
    }
    
    results <- count.generalised(results, get.No(results))
    
    return( results[, order(names(results))] )
}

count.generalised <- function(df, N) {
    target.names = paste('test', ERR_TGT_INFIX, 0:(N-1), sep='')
    count.names = paste('gen_tgt_', 0:(N-1), sep='')
    df[count.names] <- FALSE
    for(i in (1:N)) {
        df[count.names[i]] <- df[target.names[i]] == 0
    }
    return(df)
}

vplayout <- function(x, y) viewport(layout.pos.row = x, layout.pos.col = y)

#extract legend
get.legend <- function(plt) {
    gt <- ggplotGrob(plt)
    idx <- grep('guide', gt$layout$name)
    if (length(idx) > 1)
        stop('More than one match for pattern \"guide\"')
    return( gt$grobs[[idx]] )
}

get.No <- function(results) {
    if(min(results$No) == max(results$No)) {
        return(min(results$No))
    }
    else {
        stop('Different values for number of outputs in results.')
    }
}

plot.err <- function(results, perbit, err.type, by, use.notch=FALSE, show.legend=TRUE,
                     colour.start=0, legend.pos=c(.12, .85), legend.cols = 1) {
    N <- get.No(results)
    if(perbit) {
        if(by=='lf' || by=='learner>gf' || by=='gf>learner') {
            results$grp <- factor(paste(results$learner, results$guiding_function, sep=' / '))
            legend.name <- 'Learner / Guiding Function'
        }
        else if(by=='learner') {
            results$grp <- results$learner
            legend.name <- 'Learner'
        }
        else if(by=='gf'){
            results$grp <- results$guiding_function
            legend.name <- 'Guiding Function'
        }
        else if(by=='tf') {
            results$grp <- results$transfer_functions
            legend.name <- 'Transfer function'
        }
        else {
            stop('unsupported value for \"by\"')
        }
        if(err.type == 'test') {
            target.names = paste('test', ERR_TGT_INFIX, 0:(N-1), sep='')
            labels <- labs(x = 'Target', y = 'Test error') 
        }
        else if(err.type == 'train') {
            target.names = paste('train', ERR_TGT_INFIX, 0:(N-1), sep='')
            labels <- labs(x = 'Target', y = 'Training error') 
        }
        else {
            stop('unsupported value for \"err.type\"')
        }
        # data for errors
        cols.to.keep <- c('grp', target.names)
        error.data <- melt(subset(results, select = cols.to.keep), id.vars='grp')
        # full per bit plot
        p <- ggplot(error.data, aes(x=variable, y=value, color=grp)) + 
            labels +
            scale_x_discrete(breaks=target.names, labels=(1:N)) + 
            scale_color_hue(h.start=colour.start, name=legend.name)
    }
    else {
        if(err.type == 'test') {
            # Test Error (simple) plot
            if(by=='lf') {
                results$grp <- factor(paste(results$learner, results$guiding_function, sep=' / '))            
                p <- ggplot(results, aes(x=grp, y=test_error_simple, color=grp)) + 
                    labs(x = 'Learner / Guiding Function', y = 'Test error') + 
                    scale_color_hue(h.start=colour.start, name='Learner / Guiding Function')
            }
            else if(by=='learner>gf') {
                p <- ggplot(results,aes(x=guiding_function, y=test_error_simple, color=learner)) +
                    labs(x = 'Guiding Function', y = 'Test error') +
                    scale_color_hue(h.start=colour.start, name='Learner')
            }
            else if(by=='gf>learner') {
                p <- ggplot(results,aes(x=learner, y=test_error_simple, color=guiding_function)) +
                    labs(x = 'Learner', y = 'Test error') +
                    scale_color_hue(h.start=colour.start, name='Guiding Function')
            }
            else if(by=='learner') {
                p <- ggplot(results,aes(x=learner, y=test_error_simple, color=learner)) +
                    labs(x = 'Learner', y = 'Test error')
            }
            else if(by=='gf'){
                p <- ggplot(results,aes(x=guiding_function, y=test_error_simple, color=guiding_function)) +
                    labs(x = 'Guiding Function', y = 'Test error')
            }
            else if(by=='tf') {
                p <- ggplot(results,aes(x=transfer_functions, y=test_error_simple, color=transfer_functions)) +
                    labs(x = 'Transfer function', y = 'Test error')
            }
            else {
                stop('unsupported value for \"by\"')
            }
            
            #p <- p + theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01))
        }
        else if(err.type == 'train') {
            # training error
            if(by=='lf') {
                results$grp <- factor(paste(results$learner, results$guiding_function, sep=' / '))            
                p <- ggplot(results, aes(x=grp, y=training_error_simple, color=grp)) + 
                    labs(x = 'Learner / Guiding Function', y = 'Training error') + 
                    scale_color_hue(h.start=colour.start, name='Learner / Guiding Function')
            }
            else if(by=='learner>gf') {
                p <- ggplot(results,aes(x=guiding_function, y=training_error_simple, color=learner)) + 
                    labs(x = 'Guiding Function', y = 'Training error') + 
                    scale_color_hue(h.start=colour.start, name='Learner')
            }
            else if(by=='gf>learner') {
                p <- ggplot(results,aes(x=learner, y=training_error_simple, color=guiding_function)) + 
                    labs(x = 'Learner', y = 'Training error') + 
                    scale_color_hue(h.start=colour.start, name='Guiding Function')
            }
            else if(by=='learner') {
                p <- ggplot(results,aes(x=learner, y=training_error_simple, color=learner)) +
                    labs(x = 'Learner', y = 'Training error')
            }
            else if(by=='gf'){
                p <- ggplot(results,aes(x=guiding_function, y=training_error_simple, color=guiding_function)) +
                    labs(x = 'Guiding Function', y = 'Training error')
            }
            else if(by=='tf') {
                p <- ggplot(results,aes(x=transfer_functions, y=training_error_simple, color=transfer_functions)) +
                    labs(x = 'Transfer function', y = 'Training error')
            }
            else {
                stop('unsupported value for \"by\"')
            }
            
            #p <- p + theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01))
        }
        else {
            stop('unsupported value for \"err.type\"')
        }
    }
    
    #p <- p + geom_point() + 
    p <- p + geom_boxplot(notch=use.notch) +
        theme(legend.position=legend.pos) +
        guides(color=guide_legend(ncol=legend.cols, byrow=FALSE))
    
    print(p)
    return(p)
}

plot.err.vs.target.line <- function(results, by, func, colour.start=0, legend.pos=c(.12, .85)) {
    N <- get.No(results)
    if(by=='learner+gf' || by=='lf') {
        results$grp <- factor(paste(results$learner, results$guiding_function, sep=' / '))
        legend.name <- 'Learner / Guiding Function'
    }
    else if(by=='learner') {
        results$grp <- results$learner
        legend.name <- 'Learner'
    }
    else if(by=='gf'){
        results$grp <- results$guiding_function
        legend.name <- 'Guiding Function'
    }
    else {
        stop('unsupported value for \"by\"')
    }
    
    # full error per bit plot    
    # data for errors
    target.names = paste('test', ERR_TGT_INFIX, 0:(N-1), sep='')
    cols.to.keep <- c('grp', target.names)
    error.data <- melt(subset(results, select = cols.to.keep), id.vars='grp')
    
    # change test_error_target_n   ->   n
    error.data$variable <- mapvalues(error.data$variable,
                                     from=paste('test', ERR_TGT_INFIX, 0:(N-1), sep=''),
                                     to = 0:(N-1))
    error.data$variable <- as.numeric(as.character(error.data$variable))
    # apply function to aggregated data
    agg.err.dat = aggregate(value~grp+variable, error.data, func)
    
    p <- ggplot(agg.err.dat, aes(x=variable, y=value, color=grp)) + 
        geom_line() + 
        labs(x = 'Target', y = 'Test error') + 
        scale_color_hue(h.start=colour.start, name=legend.name) +
        theme(legend.position=legend.pos, legend.key=element_blank()) 
        #theme(legend.position=legend.pos, legend.key=element_blank(), 
        #      text = element_text(family='CM Roman', size=12))
    print(p)
    return(p)
}

plot.gen.rate.vs.target <- function(results, plot.type='line', colour.start=0, legend.pos=c(.12, .85)) {
    N <- get.No(results)
    names = paste('tz', 0:(N-1), sep='')
    f <- paste('cbind(', paste(names, collapse=', '), ') ~', 'learner + guiding_function')
    agg <- aggregate(as.formula(f), data=results, FUN=mean)
    agg <- melt(agg, id=c('learner', 'guiding_function'))
    agg$grp <- factor(paste(agg$learner, agg$guiding_function, sep=' / '))
    if(plot.type == 'bar') {
        p <- ggplot(agg, aes(x=variable, y=value, fill=grp)) +
            geom_bar(stat='identity', position=position_dodge(), colour='black')
    }
    else if(plot.type == 'line') {
        p <- ggplot(agg, aes(x=variable, y=value, colour=grp)) +
            geom_line(aes(group=grp))        
    }
    else {
        stop('unsupported value for \"plot.type\"')
    }
        
    p <- p + scale_x_discrete(labels=(1:8)) +
        scale_fill_discrete(name='Learner / Guiding Function') +
        labs(x = 'Target', y = 'Perfect generalisation rate')
    print(p)
    return(p)
}

plot3.errs.gf <- function(results, use.notch=TRUE, show.legend=TRUE) {
    colour.start <- 0
    N <- get.No(results)
    # depth plot
#     cols.to.keep <- c('guiding_function', paste('max_depth_target_', 0:(N-1), sep=''))
#     depth.data <- melt(subset(results, select = cols.to.keep), id.vars='guiding_function')
#     plot.depth <- ggplot(depth.data) + geom_boxplot(aes(x=variable, y=value, color=guiding_function))
    
    # data for errors
    target.names = paste('test', ERR_TGT_INFIX, 0:(N-1), sep='')
    cols.to.keep <- c('guiding_function', target.names)
    error.data <- melt(subset(results, select = cols.to.keep), id.vars='guiding_function')
    
    # full error per bit plot
    plot.err.per.bit <- ggplot(error.data, aes(x=variable, y=value, color=guiding_function)) + 
        geom_boxplot(notch=use.notch) + 
        labs(title = 'Test error per target', x = 'target', y = 'error') + 
        scale_x_discrete(breaks=target.names, labels=(1:N)) + 
        scale_color_hue(h.start=colour.start, name='Guiding Function')

    # Test Error (simple) plot
    plot.test.err <- ggplot(results,aes(x=guiding_function, y=test_error_simple, color=guiding_function)) + 
        geom_boxplot(notch=use.notch) +
        labs(title = 'Test error', x = 'Guiding Function', y = 'error') + 
        theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) + 
        scale_color_hue(h.start=colour.start, name='Guiding Function')
    
    # training error
    plot.training.err <- ggplot(results,aes(x=guiding_function, y=training_error_simple, color=guiding_function)) + 
        geom_boxplot() +
        labs(title = 'Training error', x = 'Guiding Function', y = 'error') + 
        theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) + 
        scale_color_hue(h.start=colour.start, name='Guiding Function')
    
    # get common legend
    legend <- editGrob(get.legend(plot.err.per.bit), vp = vplayout(1:2, 3))
    # remove legends
    plot.err.per.bit <- plot.err.per.bit + theme(legend.position='none')
    plot.test.err <- plot.test.err + theme(legend.position='none')
    plot.training.err <- plot.training.err + theme(legend.position='none')
    # generate 3 part plot with common legend
    grid.newpage()
    cols <- if(show.legend) 3 else 2
    pushViewport(viewport(layout = grid.layout(nrow = 2, ncol = cols,
                                               widths = unit(c(2, 2, 0.6)[1:cols], c('null', 'null')),
                                               heights = unit(c(1.3, 1)[1:cols], c('null', 'null')))))
    print(plot.err.per.bit, vp = vplayout(1, 1:2))
    print(plot.test.err, vp = vplayout(2, 1))
    print(plot.training.err, vp = vplayout(2, 2))
    if(show.legend) {
        grid.draw(legend)
    }
}

plot.errs.by.sample <- function(results) {
    p.test <- ggplot(aes(x=num.Ne, y=test_error_simple, color=guiding_function), data=results) + 
        geom_boxplot() +
        labs(title = 'Test error', x = 'Ne', y = 'error')
    
    
    p.training <- ggplot(aes(x=num.Ne, y=training_error_simple, color=guiding_function), data=results) + 
        geom_boxplot() +
        labs(title = 'Training error', x = 'Ne', y = 'error') +
        theme(axis.title.y = element_blank())
        
    # get common legend
    # get common legend
    legend <- editGrob(get.legend(p.test), vp = vplayout(1, 3))
    # remove legends
    p.test <- p.test + theme(legend.position='none')
    p.training <- p.training + theme(legend.position='none')
    # generate 3 part plot with common legend
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow = 1, ncol = 3,
                                               widths = unit(c(2, 2, 0.6), c('null', 'null')),
                                               heights = unit(c(1), c('null', 'null')))))
    print(p.test, vp = vplayout(1, 1))
    print(p.training, vp = vplayout(1, 2))
    grid.draw(legend)
}

plot.single.comparison <- function(results) {
  # create factor from numeric
  p.test <- ggplot(aes(x=optimiser_name, y=test_error_simple, color=optimiser_name), data=results) + 
    geom_boxplot(notch=TRUE) +
    labs(title = 'Test error', x = 'optimiser', y = 'error') + 
    scale_color_discrete(name='Optimiser')
  
  p.training <- ggplot(aes(x=optimiser_name, y=training_error_simple, color=optimiser_name), data=results) + 
    geom_boxplot(notch=FALSE) +
    labs(title = 'Training error', x = 'optimiser', y = 'error') +
    theme(axis.title.y = element_blank())
  
  p.iterations <- ggplot(aes(x=optimiser_name, y=total_iterations, color=optimiser_name), data=results) + 
    geom_boxplot(notch=TRUE) +
    labs(title = 'Total steps', x = 'optimiser', y = 'steps')
  
  # get common legend
  # get common legend
  # generate 3 part plot with common legend
  grid.newpage()
  pushViewport(viewport(layout = grid.layout(nrow = 2, ncol = 2,
                                             widths = unit(c(2, 2), c('null', 'null')),
                                             heights = unit(c(1, 1), c('null', 'null')))))
  legend <- editGrob(get.legend(p.test), vp = vplayout(2, 2))
  # remove legends
  p.test <- p.test + theme(legend.position='none')
  p.training <- p.training + theme(legend.position='none')
  p.iterations <- p.iterations + theme(legend.position='none')
  
  print(p.test, vp = vplayout(1, 1))
  print(p.training, vp = vplayout(1, 2))
  print(p.iterations, vp = vplayout(2, 1))
  grid.draw(legend)
}

list_lengths <- function(x) {
    if(is.null(x)) {
        return(NULL)
    }
    else {
        return(lapply(x, length))
    }
}

