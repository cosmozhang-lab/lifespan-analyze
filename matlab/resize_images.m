function [] = resize_images()
params;
load(fullfile(outdir, [plate, '.out.mat']));
if ~exist(fullfile(outdir, [plate, '.resize']), 'dir')
    mkdir(fullfile(outdir, [plate, '.resize']));
end
for i = 1:nfiles
    name = dirnames{i};
    tofilepath = fullfile(outdir, [plate, '.resize'], [name, suffix]);
    if ~exist(tofilepath, 'file');
        img = imread(fullfile(outdir, plate, [name, suffix]));
        img = imresize(img, sc);
        imwrite(img, tofilepath);
    end
    fprintf('%d/%d\n', i, nfiles);
end
end

