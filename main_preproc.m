mmts_bw = zeros([imagesize, nfiles], 'uint8');

% single frame - segmentation of C. elegans
for i = 1:nfiles
    bw = detect_worm_2d(mmts(:, :, i), minsize, maxsize);
    mmts_bw(:, :, i) = bw;
    if verbose >= 10
        fprintf('detected %d / %d\n', i, nfiles);
    end
end