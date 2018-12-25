function [] = results_to_tiff()

params;

load(fullfile(outdir, [plate, '.out.mat']));

figure;
for idx = 1:nfiles
    name = dirnames{idx};
    img = imread(fullfile(outdir, plate, [name, suffix]));
    imshow(image_shift(img, fliplr(imshifts(idx,:))));
    if ~isempty(centroids); ctds = centroids{idx}; else; ctds = []; end
    if ~isempty(oricentroids); octds = oricentroids{idx}; else; octds = []; end
    if ~isempty(wormcentroids); wctds = wormcentroids{idx}; else; wctds = []; end
    if ~isempty(wctds)
        hold on;
        plot(wctds(:,2), wctds(:,1), '.', 'Color', [0,1,0]);
        hold off;
    end
    if ~isempty(octds)
        hold on;
        plot(octds(:,2), octds(:,1), 'b*');
        hold off;
    end
    if ~isempty(ctds)
        hold on;
        plot(ctds(:,2), ctds(:,1), 'ro');
        hold off;
    end
    name = strrep(name, '__', 'T');
    title(sprintf('%d/%d  %s', idx, nfiles, name));
    frame = getframe(gcf);
    pause;
end

end

