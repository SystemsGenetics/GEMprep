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
emx = read.table(INFILE, header=TRUE, row.names=1)

# replace zeros with NA
for (i in names(emx)) {
  emx[[i]][which(emx[[i]] == 0)] = NA
}

print("Performing log2 transform...")

# perform log2 transform
emx = log2(emx)

print("Plotting sample distributions...")

# plot sample distributions (pre-normalization)
png(PLOTFILE_DENSITY_PRE, width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
colors <- rainbow(106)

plot(density((emx[,1]), na.rm=TRUE), xlab="log count")
for (i in 1:ncol(emx)) {
  lines(density((emx[,i]), na.rm=TRUE), col=colors[i])
}

print("Performing K-S test and outlier removal...")

# compute the global sample distribution
g = emx[, 1]
for (i in 2:ncol(emx)) {
  g = c(g, emx[, i])
}

# perform K-S test between each sample and the global distribution
ks_test = numeric()
for (i in 1:ncol(emx)) {
  ks_test[i] = ks.test(emx[, i], g)["statistic"]
}

ksdf = data.frame(names(emx), unlist(ks_test))
colnames(ksdf) = c('sample', 'ks_dvalue')
row.names(ksdf) = c(1:ncol(emx))

# remove the outlier samples (D > 0.15)
ks_threshold = 0.15
emx = emx[,which(ksdf$ks_dvalue < ks_threshold)]

print("Performing quantile normalization...")

# split dataframe into matrix, rownames, and colnames
emx_rownames <- row.names(emx)
emx_colnames = colnames(emx)
emx <- data.matrix(emx, rownames.force=NA)

# perform quantile normalization
emx <- normalize.quantiles(emx, copy=FALSE)

# convert normalized matrix back into dataframe
emx <-as.data.frame(emx, row.names=emx_rownames, col.names=cmx_colnames)

print("Plotting sample distributions...")

# plot sample distributions (post-normalization)
png(PLOTFILE_DENSITY_POST, width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
colors <- rainbow(106)
plot(density((emx[,1]), na.rm=TRUE), xlab="log count")
for (i in 1:ncol(emx)) {
  lines(density((emx[,i]), na.rm=TRUE), col=colors[i])
}

# plot global distribution
png("GEM-density-combined.png", width=8, height=8, units="in", res=300)
par(mar=c(2,2,2,2))
plot(density((g), na.rm=TRUE), xlab="log count")

print("Saving output expression matrix and K-S test results...")

# save normalized matrix and K-S test results
write.table(emx, OUTFILE, append=FALSE, quote=FALSE, sep="\t")
write.table(ksdf, OUTFILE_KS, append=FALSE, quote=FALSE, sep="\t")
