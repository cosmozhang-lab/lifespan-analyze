function [] = resize_images()
params;
load(fullfile(outdir, [plate, '.out.mat']));
if ~exist(fullfile(outdir, [plate, '.resize']), 'dir')
    mkdir(fullfile(outdir, [plate, '.resize']));
end
if ~exist(fullfile(outdir, [plate, '.resize']), 'dir'); mkdir(fullfile(outdir, [plate, '.resize'])); end
for i = 1:nfiles
    name = dirnames{i};
    if ~exist(fullfile(outdir, [plate, '.resize'], name), 'dir'); mkdir(fullfile(outdir, [plate, '.resize'], name)); end
    tofilepath = fullfile(outdir, [plate, '.resize'], name, [plate, suffix]);
    if ~exist(tofilepath, 'file');
        img = imread(fullfile(outdir, plate, name, [plate, suffix]));
        img = imresize(img, sc);
        imwrite(img, tofilepath);
    end
    fprintf('%d/%d\n', i, nfiles);
end
end

