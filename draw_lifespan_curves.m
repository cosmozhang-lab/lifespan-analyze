main_params;

% plates = {'G10','G11','G12', 'H10','H11','H12','I10','I11','I12',};
plates = {'G11','H10','H12','I10','I12',};
figsize = [0 0 11 11];

time_interval = 8;
start_time = 9 * 24;

fontsize = 18;
fontname = 'Candara';
linewidth = 2;

thecurves = zeros(length(plates), nfiles);

main_params;
figure(1);
for iplt = 1:length(plates)
main_params;
plate = plates{iplt};
load(sprintf('out/result-%s.mat', plate));
% num_deaths = max(num_deaths - 1, 0);
num_deaths(53:end) = 0;
numalive = cumsum(num_deaths);
numalive = numalive(end) - numalive;
isdaf2 = 0;
lw = linewidth;
if strcmpi(plate, 'I11')
    lw = linewidth * 3;
    isdaf2 = 1;
end
numalive_ratio = numalive / numalive(1);
ha = plot(((0:nfiles-1) * time_interval + start_time)/24, numalive_ratio, 'LineWidth', linewidth);
thecurves(iplt, :) = numalive_ratio;
if isdaf2
    ax_daf2 = ha;
elseif iplt == 1
    ax_wt = ha;
end
hold on;
end
hold off;

% legend([ax_daf2, ax_wt], 'daf-2', 'wt');

hold on;
plot([0,start_time]/24, [1,1], 'Color', [1 1 1] * 0.5, 'LineWidth', linewidth);
plot([start_time,start_time]/24, [0,1], '--', 'Color', [1 1 1] * 0.5, 'LineWidth', linewidth);
hold off;

% set(gca, 'XMinorTick', 'on');
% set(gca, 'YMinorTick', 'on');

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

save('out/curves.mat', 'thecurves');