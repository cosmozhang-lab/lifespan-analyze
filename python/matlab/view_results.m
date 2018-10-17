function [] = view_results()

params;

load(fullfile(outdir, 'out.mat'));

numdeaths(isnan(numdeaths)) = 0;
numalive = cumsum(numdeaths);
numalive = numalive(end) - numalive;

figure(1);
plot(numalive);

figure(2);
for i = 1:nfiles
    imshow(image_shift(imread(fullfile(outdir, plate, [dirnames{i} '.tiff'])), fliplr(imshifts(i,:))));
    ctds = centroids{i};
    octds = oricentroids{i};
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
    title(sprintf('%d/%d', i, nfiles));
    pause;
end

end