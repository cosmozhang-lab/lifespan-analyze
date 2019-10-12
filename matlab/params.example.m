% Where to find the result file and the images.
% If you don't want to specify this option, set it as ''.
rootdir = '/disk1/home/cosmo/downloads/lifespan';
% Result MAT filename.
% Final result filename will be formed as
% <rootdir>/<resultfile>
resultfile = 'G7.out.mat';
% Image filenames' prefix and suffix.
% Final image filename will be formed as
% <rootdir>/<prefix><datetime><suffix>.
imgprefix = 'G4\\G4__';
imgsuffix = '.tiff';
% Frames per day
framerate = 24;
% Image scaling factor.
% If you use resized images instead of the original
% images, you must specify it here. Otherwise leave
% it as 1.
sc = 1;
% Frames per day
framerate = 24;
% Maximum number of files to watch.
maxnfiles = Inf;
