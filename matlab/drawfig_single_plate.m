main_params;
load('./out/result-H12.mat');

markersize = 6;
figsize = [0 0 8 8];
markeroffset = [0 100];

files = get_file_list(plate);
files = files(end-nfiles+1:end);

% numalive = cumsum(num_deaths);
% numalive = numalive(end) - numalive;
% 
% figure(1);
% plot(numalive);

for i = 5
    thefile = files(i);
    im = imread(thefile.fullpath);
    im = image_shift(im, imshifts(i,:));
    figure(2);
    imshow(im);
    ctds = centroids_before_exclude{i} + markeroffset;
    ctdsori = centroids_origin{i} + markeroffset;
    if ~isempty(ctdsori)
        hold on;
        plot(ctdsori(:,1), ctdsori(:,2), '^',...
            'MarkerEdgeColor', 'None',...
            'MarkerFaceColor', 'b',...
            'MarkerSize', markersize);
        hold off;
    end
%     if ~isempty(ctds)
%         hold on;
%         plot(ctds(:,1), ctds(:,2), '^',...
%             'MarkerEdgeColor', 'None',...
%             'MarkerFaceColor', 'r',...
%             'MarkerSize', markersize);
%         hold off;
%     end
    text('String', thefile.subdir, 'Position', [1 1], 'Units', 'normalized', 'HorizontalAlignment', 'right');
    set(gcf, 'unit', 'inches');
    set(gcf, 'position', figsize);
    set(gca, 'position', [0 0 1 1]);
    print(sprintf('figures/%s[%s].jpg', plate, thefile.subdir), '-djpeg', '-r125');
end
