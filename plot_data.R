library(ggplot2)
library(jsonlite)
library(reshape2)
library(tcltk)
library(grid)
library(plyr)

options(stringsAsFactors = TRUE)

ERR_TGT_INFIX <- "_err_tgt_"

get_results <- function(file_name=NULL) {
    options(stringsAsFactors = TRUE)
    if(is.null(file_name)) {
        file_name <- tk_choose.files(
            default = "HMRI/experiments/results", caption = "Select experiment file", multi = FALSE,
            filters=matrix(c("json", ".json"), 1, 2, byrow = TRUE))
        print(file_name)
    }
    results <- fromJSON(file_name)
    if("final_network" %in% colnames(results)) {
        results <- subset(results, select = -c(final_network))
    }
    ind <- sapply(results, is.character)
    results[ind] <- lapply(results[ind], factor)
    # reorganise function factor
    # results$guiding_function <- factor(
    #     results$optimiser_guiding_function,
    #     levels = levels(results$optimiser_guiding_function)[
            # c(1, 2, 4, 6, 8, 10, 12, 3, 5, 7, 9, 11, 13)])
    # create factor from numeric
    results$num.Ne <- factor(results$Ne)

    if(class(results$total_iterations) == "list") {
        # something like the below
        for (i in 1:nrow(results)) {
            results$total_it[i] <- do.call(sum, results$total_iterations[i])
        }
    }
    else {
        results$total_it <- results$total_iterations
    }

    results <- count_generalised(results, get_No(results))

    return( results[, order(names(results))] )
}

count_generalised <- function(df, N) {
    target_names <- paste("test", ERR_TGT_INFIX, 0:(N - 1), sep="")
    count_names <- paste("gen_tgt_", 0:(N - 1), sep="")
    df[count_names] <- FALSE
    for (i in (1:N)) {
        df[count_names[i]] <- df[target_names[i]] == 0
    }
    return(df)
}

vplayout <- function(x, y) viewport(layout.pos.row = x, layout.pos.col = y)

#extract legend
get_legend <- function(plt) {
    gt <- ggplotGrob(plt)
    idx <- grep("guide", gt$layout$name)
    if (length(idx) > 1)
        stop("More than one match for pattern \"guide\"")
    return( gt$grobs[[idx]] )
}

get_No <- function(results) {
    if(min(results$No) == max(results$No)) {
        return(min(results$No))
    }
    else {
        stop("Different values for number of outputs in results.")
    }
}

plot.err <- function(
    results, perbit, err.type, by, use.notch=FALSE, show.legend=TRUE,
    colour_start=0, legend.pos=c(.12, .85), legend.cols = 1) {

    N <- get_No(results)
    legend_label <- NULL

    if(err.type == "test") {
        y <- "test_error_simple"
        y_label <- "Training error"
    }
    else if(err.type == "train") {
        y <- "training_error_simple"
        y_label <- "Test error"
    }
    else {
        stop("unsupported value for \"err.type\"")
    }

    if(perbit) {
        if(by == "lf" || by == "learner>gf" || by == "gf>learner") {
            results$grp <- factor(paste(results$learner,
                                        results$guiding_function,
                                        sep=" / "))
            legend_label <- "Learner / Guiding Function"
        }
        else if(by == "learner") {
            results$grp <- results$learner
            legend_label <- "Learner"
        }
        else if(by == "gf"){
            results$grp <- results$guiding_function
            legend_label <- "Guiding Function"
        }
        else if(by == "tf") {
            results$grp <- results$transfer_functions
            legend_label <- "Transfer function"
        }
        else {
            stop("unsupported value for \"by\"")
        }

        x_label <- "Target"
        target_names <- paste(err.type, ERR_TGT_INFIX, 0:(N - 1), sep="")


        # data for errors
        cols_to_keep <- c("grp", target_names)
        error_data <- melt(subset(results, select=cols_to_keep), id.vars="grp")
        # full per bit plot
        p <- ggplot(error_data, aes(x=variable, y=value, color=grp)) +
            scale_x_discrete(breaks=target_names, labels = (1:N))
    }
    else {
        if(by == "lf") {
            results$grp <- factor(paste(
                results$learner, results$guiding_function, sep=" / "))
            x <- colour <- "grp"
            x_label <- legend_label <- "Learner / Guiding Function"
        }
        else if(by == "learner>gf") {
            x <- "guiding_function"
            colour <- "learner"
            x_label <- "Guiding Function"
            legend_label <- "Learner"
        }
        else if(by == "gf>learner") {
            x <- "learner"
            colour <- "guiding_function"
            x_label <- "Learner"
            legend_label <- "Guiding Function"
        }
        else if(by == "learner") {
            x <- colour <- "learner"
            x_label <- "Learner"
        }
        else if(by == "gf"){
            x <- colour <- "guiding_function"
            x_label <- "Guiding Function"
        }
        else if(by == "tf") {
            x <- colour <- "transfer_functions"
            x_label <- "Transfer function"
        }
        else {
            stop("unsupported value for \"by\"")
        }

        p <- ggplot(results, aes_string(x, y, colour=colour))
    }

    p <- p + labs(x=x_label, y=y_label) +
        geom_boxplot(notch=use.notch) +
        theme(legend.position=legend.pos) +
        guides(color=guide_legend(ncol=legend.cols, byrow=FALSE))

    if(! is.null(legend_label)) {
        p <- p + scale_color_hue(h.start=colour_start, name=legend_label)
    }

    print(p)
    return(p)
}

plot_err_vs_target_line <- function(results, by, func, colour_start=0,
                                    legend_pos=c(.12, .85)) {
    N <- get_No(results)
    if(by == "learner+gf" || by == "lf") {
        results$grp <- factor(paste(results$learner, results$guiding_function,
                                    sep=" / "))
        legend.name <- "Learner / Guiding Function"
    }
    else if(by == "learner") {
        results$grp <- results$learner
        legend.name <- "Learner"
    }
    else if(by == "gf"){
        results$grp <- results$guiding_function
        legend.name <- "Guiding Function"
    }
    else {
        stop("unsupported value for \"by\"")
    }

    # full error per bit plot
    # data for errors
    target_names <- paste("test", ERR_TGT_INFIX, 0:(N - 1), sep="")
    cols_to_keep <- c("grp", target_names)
    error.data <- melt(subset(results, select = cols_to_keep), id.vars="grp")

    # change test_error_target_n   ->   n
    error.data$variable <- mapvalues(
        error.data$variable, to=0:(N - 1),
        from=paste("test", ERR_TGT_INFIX, 0:(N - 1), sep=""))
    error.data$variable <- as.numeric(as.character(error.data$variable))
    # apply function to aggregated data
    agg_err_data <- aggregate(value ~ grp + variable, error.data, func)

    p <- ggplot(agg_err_data, aes(x=variable, y=value, color=grp)) +
        geom_line() +
        labs(x = "Target", y = "Test error") +
        scale_color_hue(h.start=colour_start, name=legend.name) +
        theme(legend.position=legend_pos, legend.key=element_blank())
        #theme(legend.position=legend.pos, legend.key=element_blank(),
        #      text = element_text(family="CM Roman", size=12))
    print(p)
    return(p)
}

plot_gen_rate_vs_target <- function(results, plot_type="line", colour_start=0,
                                    legend.pos=c(.12, .85)) {
    N <- get_No(results)
    names <- paste("tz", 0:(N - 1), sep="")
    f <- paste("cbind(", paste(names, collapse=", "),
               ") ~", "learner + guiding_function")
    agg <- aggregate(as.formula(f), data=results, FUN=mean)
    agg <- melt(agg, id=c("learner", "guiding_function"))
    agg$grp <- factor(paste(agg$learner, agg$guiding_function, sep=" / "))
    if(plot_type == "bar") {
        p <- ggplot(agg, aes(x=variable, y=value, fill=grp)) +
            geom_bar(stat="identity", position=position_dodge(), colour="black")
    }
    else if(plot_type == "line") {
        p <- ggplot(agg, aes(x=variable, y=value, colour=grp)) +
            geom_line(aes(group=grp))
    }
    else {
        stop("unsupported value for \"plot_type\"")
    }

    p <- p + scale_x_discrete(labels=(1:8)) +
        scale_fill_discrete(name="Learner / Guiding Function") +
        labs(x = "Target", y = "Perfect generalisation rate")
    print(p)
    return(p)
}

plot3_errs_gf <- function(results, use.notch=TRUE, show.legend=TRUE) {
    colour_start <- 0
    N <- get_No(results)

    # data for errors
    target_names <- paste("test", ERR_TGT_INFIX, 0:(N - 1), sep="")
    cols_to_keep <- c("guiding_function", target_names)
    error.data <- melt(subset(results, select = cols_to_keep),
                       id.vars="guiding_function")

    # full error per bit plot
    plot_err_per_bit <- ggplot(error.data,
        aes(x=variable, y=value, color=guiding_function)) +
        geom_boxplot(notch=use.notch) +
        labs(title = "Test error per target", x = "target", y = "error") +
        scale_x_discrete(breaks=target_names, labels=(1:N)) +
        scale_color_hue(h.start=colour_start, name="Guiding Function")

    # Test Error (simple) plot
    plot_test_err <- ggplot(results,
        aes(x=guiding_function, y=test_error_simple, color=guiding_function)) +
        geom_boxplot(notch=use.notch) +
        labs(title = "Test error", x = "Guiding Function", y = "error") +
        theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) +
        scale_color_hue(h.start=colour_start, name="Guiding Function")

    # training error
    plot_train_err <- ggplot(results,
        aes(x=guiding_function, y=training_error_simple, color=guiding_function)) +
        geom_boxplot(notch=use.notch) +
        labs(title = "Training error", x = "Guiding Function", y = "error") +
        theme(axis.text.x=element_text(angle=45, vjust=1.1, hjust=1.01)) +
        scale_color_hue(h.start=colour_start, name="Guiding Function")

    # get common legend
    legend <- editGrob(get_legend(plot_err_per_bit), vp=vplayout(1:2, 3))
    # remove legends
    plot_err_per_bit <- plot_err_per_bit + theme(legend.position="none")
    plot_test_err <- plot_test_err + theme(legend.position="none")
    plot_train_err <- plot_train_err + theme(legend.position="none")
    # generate 3 part plot with common legend
    grid.newpage()
    cols <- if(show.legend) 3 else 2
    pushViewport(viewport(layout = grid.layout(
        nrow = 2, ncol = cols,
        widths = unit(c(2, 2, 0.6)[1:cols], c("null", "null")),
        heights = unit(c(1.3, 1)[1:cols], c("null", "null")))))
    print(plot_err_per_bit, vp = vplayout(1, 1:2))
    print(plot_test_err, vp = vplayout(2, 1))
    print(plot_train_err, vp = vplayout(2, 2))
    if(show.legend) {
        grid.draw(legend)
    }
}

plot_errs_by_sample <- function(results) {
    ptest <- ggplot(results,
        aes(x=num.Ne, y=test_error_simple, color=guiding_function)) +
        geom_boxplot() +
        labs(title = "Test error", x = "Ne", y = "error")

    ptrain <- ggplot(results,
        aes(x=num.Ne, y=training_error_simple, color=guiding_function)) +
        geom_boxplot() +
        labs(title = "Training error", x = "Ne", y = "error") +
        theme(axis.title.y = element_blank())

    # get common legend
    # get common legend
    legend <- editGrob(get_legend(ptest), vp = vplayout(1, 3))
    # remove legends
    ptest <- ptest + theme(legend.position="none")
    ptrain <- ptrain + theme(legend.position="none")
    # generate 3 part plot with common legend
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(
        nrow = 1, ncol = 3,
        widths = unit(c(2, 2, 0.6), c("null", "null")),
        heights = unit(c(1), c("null", "null")))))
    print(ptest, vp = vplayout(1, 1))
    print(ptrain, vp = vplayout(1, 2))
    grid.draw(legend)
}


plot_single_comparison <- function(results) {
  # create factor from numeric
  p_test <- ggplot(results,
    aes(x=optimiser_name, y=test_error_simple, color=optimiser_name)) +
    geom_boxplot(notch=TRUE) +
    labs(title = "Test error", x = "optimiser", y = "error") + 
    scale_color_discrete(name="Optimiser")

  p_train <- ggplot(results,
    aes(x=optimiser_name, y=training_error_simple, color=optimiser_name)) +
    geom_boxplot(notch=FALSE) +
    labs(title = "Training error", x = "optimiser", y = "error") +
    theme(axis.title.y = element_blank())

  p_iters <- ggplot(results,
    aes(x=optimiser_name, y=total_iterations, color=optimiser_name)) +
    geom_boxplot(notch=TRUE) +
    labs(title = "Total steps", x = "optimiser", y = "steps")

  # generate 3 part plot with common legend
  grid.newpage()
  pushViewport(viewport(layout = grid.layout(
    nrow = 2, ncol = 2,
    widths = unit(c(2, 2), c("null", "null")),
    heights = unit(c(1, 1), c("null", "null")))))
  legend <- editGrob(get_legend(p_test), vp = vplayout(2, 2))
  # remove legends
  p_test <- p_test + theme(legend.position="none")
  p_train <- p_train + theme(legend.position="none")
  p_iters <- p_iters + theme(legend.position="none")

  print(p_test, vp = vplayout(1, 1))
  print(p_train, vp = vplayout(1, 2))
  print(p_iters, vp = vplayout(2, 1))
  grid.draw(legend)
}
