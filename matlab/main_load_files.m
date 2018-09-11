mmts = zeros([imagesize, nfiles], 'uint8');
files = get_file_list(plate);
files = files(end-nfiles+1:end);

% single frame - registration
mmts(:, :, 1) = imread(files(1).fullpath);
imshifts = zeros([nfiles, 2], 'double');
if verbose >= 10
    fprintf('loaded %d / %d\n', 1, nfiles);
end
for i = 2:nfiles
    imi = imread(files(i).fullpath);
    [im2shift,shifting] = match_plate(mmts(:,:,i-1), imi);
    imshifts(i,:) = shifting;
    mmts(:, :, i) = im2shift;
    if verbose >= 10
        fprintf('loaded %d / %d\n', i, nfiles);
    end
end