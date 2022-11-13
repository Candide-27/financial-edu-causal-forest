#import
library(grf)
library(sandwich)
library(lmtest)
library(Hmisc)
library(ggplot2)
library(DiagrammeR)
library(data.tree)
#Set seeds
set.seed(1) #for working with variables that need to be random
#Read files and clean-----------------------------------------------------------
RAW_PATH <- 'C:\\Personal\\Thesis\\git\\transform'
FILE <- 'Brazil2016_transform_round1_20221112194108.csv'
df <- read.csv(paste(RAW_PATH, '\\', FILE,
                     sep=''))
#Factor the school_id column
df[['cd_escola']] <- factor(df[['cd_escola']])
#Then prepare a numeric school_id column for clustering later
school_id <- as.numeric(df$cd_escola)
#Set the student id as index
rownames(df) <- df$id_geral
#Assigining outcome, treatment and covariates-----------------------------------
Y <- df$vl_proficiencia_fup #outcome
W <- df$treatment #treatment
X <- df[, - which( # - denotes the negative
  names(df) %in% c('vl_proficiencia_fup', 'treatment', 'cd_escola', 'id_geral') # thus select the col in df whose name is NOT in ...
)]
#Step1: Predict Y and W based on a prediction random forest---------------------
Y_forest <- regression_forest(
  X=X,
  Y=Y,
  clusters=school_id,
  equalize.cluster.weights = TRUE
)
#Y_predictions = Y_forest$predictions
Y_hat <- predict(Y_forest)$predictions #this returns a vector instead of data as the above
#Similar for W:
W_forest <- regression_forest(
  X=X,
  Y=W,
  clusters=school_id,
  equalize.cluster.weights = TRUE #large school receive more weights than smaller school
)
W_hat = predict(W_forest)$predictions
W_hat = predict(W_forest)$predictions
#Then do a primitve causal forest on W_hat and Y_hat--------------------------------
initial_cf <- causal_forest(
  X=X,
  Y=Y,
  W=W,
  Y.hat=Y_hat,
  W.hat=W_hat,
  clusters=school_id,
  equalize.cluster.weights = TRUE,
  tune.parameters = 'all'
)
vital_vars <- variable_importance(initial_cf)
#a weighted sum of how many time covariate i appears at the first(?) split
selected_vars <- which(vital_vars >= (mean(vital_vars)) / 1.5)

#Then grow a causal forest only on those importance variable
main_cf = causal_forest(
  X=X[, selected_vars],
  Y=Y,
  W=W,
  Y.hat=Y_hat,
  W.hat=W_hat,
  clusters=school_id,
  equalize.cluster.weights = TRUE,
  tune.parameters = 'all'
)
#The Tree-----------------------------------------------------------------------
#Get the first tree
tree = get_tree(main_cf, index=1)
#Plotting
tree_plot = plot(tree)
#Saving
cat(DiagrammeRsvg::export_svg(tree_plot), file = 'tree.svg')

#The ATE------------------------------------------------------------------------
ATE = average_treatment_effect(main_cf)
ATE[1] #return the coefficients
ATE[2] #return the standard errors
#Confidence interval

paste("95% CI for the ATE:", round(ATE[1], 3), #paste is just a join.string function
      "+/-", round(qnorm(0.975) * ATE[2], 3)) #ATE coefficient

#The CATE-----------------------------------------------------------------------
tau_hat = predict(main_cf)$predictions
# $predictions as a feature of causal_forest return the CATE for all obs in df
hist(tau_hat) #investigate the CATE distribution

#Tests for heterogeneity========================================================

#Test1 : Best Linear Predictor
test_calibration(main_cf)