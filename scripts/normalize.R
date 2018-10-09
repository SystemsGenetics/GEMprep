# install preprocessCore from bioconductor
if ( !require("preprocessCore") ) {
  source("http://bioconductor.org/biocLite.R")
  biocLite(c("preprocessCore"))
}

# load libraries
library(preprocessCore)

# define file arguments
INFILE = "FPKM.txt"
OUTFILE = "GEM.txt"
OUTFILE_KS = "GEM-ks-results.txt"
PLOTFILE_DENSITY_PRE = "GEM-density-pre.png"
PLOTFILE_DENSITY_POST = "GEM-density-post.png"

print("Loading FPKM expression matrix...")

# load input FPKM matrix
prematrix = read.table(INFILE, header=TRUE, row.names=1)

# replace zeros with NA
for (i in names(prematrix)) {
  prematrix[[i]][which(prematrix[[i]] == 0)] = NA
}

print("Performing log2 transform...")

# perform log2 transform
prematrix = log2(prematrix)

print("Plotting sample distributions...")

# plot sample distributions (pre-normalization)
png(PLOTFILE_DENSITY_PRE, width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
colors <- rainbow(106)

plot(density((prematrix[,1]), na.rm=TRUE), xlab="log count")
for (i in 1:ncol(prematrix)) {
  lines(density((prematrix[,i]), na.rm=TRUE), col=colors[i])
}

print("Performing K-S test and outlier removal...")

# compute the global sample distribution
g = prematrix[, 1]
for (i in 2:ncol(prematrix)) {
  g = c(g, prematrix[, i])
}

# perform K-S test between each sample and the global distribution
ks_test = numeric()
for (i in 1:ncol(prematrix)) {
  ks_test[i] = ks.test(prematrix[, i], g)["statistic"]
}

ksdf = data.frame(names(prematrix), unlist(ks_test))
colnames(ksdf) = c('sample', 'ks_dvalue')
row.names(ksdf) = c(1:ncol(prematrix))

# remove the outlier samples (D > 0.15)
ks_threshold = 0.15
outliers = colnames(prematrix)[which(ksdf$ks_dvalue > ks_threshold)]
ematno = prematrix[,!(names(prematrix) %in% outliers)]

print("Performing quantile normalization...")

# perform quantile normalization
umatrix <- data.matrix(ematno, rownames.force=NA)
nmatrix <- normalize.quantiles(umatrix)

# convert normalized matrix back into dataframe
GeneNames <- row.names(ematno)
SampleNames = colnames(ematno)
ematrix <-as.data.frame.matrix(nmatrix,row.names=GeneNames, optional=TRUE)
colnames(ematrix) = SampleNames

print("Plotting sample distributions...")

# plot sample distributions (post-normalization)
png(PLOTFILE_DENSITY_POST, width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
colors <- rainbow(106)
plot(density((ematrix[,1]), na.rm=TRUE), xlab="log count")
for (i in 1:ncol(ematrix)) {
  lines(density((ematrix[,i]), na.rm=TRUE), col=colors[i])
}

# plot global distribution
png("GEM-density-combined.png", width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
plot(density((g), na.rm=TRUE), xlab="log count")

print("Saving output expression matrix and K-S test results...")

# save normalized matrix and K-S test results
write.table(ksdf, OUTFILE_KS, append=FALSE, quote=FALSE, sep="\t", col.names=T)
write.table(ematrix, OUTFILE, append=FALSE, quote=FALSE, sep="\t")
