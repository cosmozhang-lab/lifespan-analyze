plates = {'G10','G11','G12', 'H10','H11','H12','I10','I11','I12',};

main_params;

for iplt = 1:length(plates)

platename = plates{iplt};
tic;
if verbose >= 5
    fprintf('Plate %s started.\n', platename);
end
plate = platename;
main_load_files;
main_preproc;
% main_save_images;
main_analyze;
tt = toc;
if verbose >= 5
    fprintf('Plate %s completed. Time used: %f\n', platename, tt);
end

end
