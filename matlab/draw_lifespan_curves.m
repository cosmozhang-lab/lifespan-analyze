main_params;

% plates = {'G10','G11','G12', 'H10','H11','H12','I10','I11','I12',};
plates = {'G11','H10','H12','I10','I12',};
groups = {...
    [1,2,3],...
    [2,3,4],...
    [3,4,5],...
    [1,3,5],...
    [2,4,5]};
figsize = [0 0 11 11];

time_interval = 8;
start_time = 9 * 24;

fontsize = 18;
fontname = 'Candara';
linewidth = 2;

thecurves = zeros(length(groups), nfiles);

plate_deaths = zeros(length(plates),nfiles);
for iplt = 1:length(plates)
plate = plates{iplt};
load(sprintf('out/result-%s.mat', plate));
plate_deaths(iplt,:) = num_deaths;
end

figure(1);
for i = 1:length(groups)
    groupiplts = groups{i};
    groupdata = plate_deaths(groupiplts,:);
    num_deaths = sum(groupdata,1);
    num_deaths(53:end) = 0;
    numalive = cumsum(num_deaths);
    numalive = numalive(end) - numalive;
    numalive_ratio = numalive / numalive(1);
    plot(((0:nfiles-1) * time_interval + start_time)/24, numalive_ratio, 'LineWidth', linewidth);
    thecurves(i, :) = numalive_ratio;
    hold on;
end
hold off;

% legend([ax_daf2, ax_wt], 'daf-2', 'wt');

hold on;
plot([0,start_time]/24, [1,1], 'Color', [1 1 1] * 0.5, 'LineWidth', linewidth);
plot([start_time,start_time]/24, [0,1], '--', 'Color', [1 1 1] * 0.5, 'LineWidth', linewidth);
hold off;

ha = gca;
ylim([0, 1.1]);
ha.YAxis.TickValues = 0:0.2:1;
ha.YAxis.MinorTick = 'on';
ha.YAxis.MinorTickValues = 0:0.1:1;
ha.YAxis.FontSize = fontsize;
ha.YAxis.FontName = fontname;
ha.YAxis.LineWidth = linewidth;
ha.YLabel.String = 'Fraction surviving';
ha.YLabel.FontSize = fontsize;
ha.YLabel.FontName = fontname;
xlim([0, 35]);
ha.XAxis.TickValues = 0:5:35;
ha.XAxis.MinorTick = 'on';
ha.XAxis.MinorTickValues = 0:1:35;
ha.XAxis.FontSize = fontsize;
ha.XAxis.FontName = fontname;
ha.XAxis.LineWidth = linewidth;
ha.XLabel.String = 'Age (days of adulthood)';
ha.XLabel.FontSize = fontsize;
ha.XLabel.FontName = fontname;

set(gcf, 'unit', 'inches');
set(gcf, 'position', [0 0 15.88 11.91] / 2.54);
print('figures/curves.jpg', '-djpeg', '-r300');
close(gcf);

% save('out/curves.mat', 'thecurves');