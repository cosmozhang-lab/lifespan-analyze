load_params;
load('./out/result.mat');

minsize = 700;
maxsize = 3500;

% files = get_file_list(plate);
% files = files(end-nfiles+1:end);

numalive = cumsum(num_deaths);
numalive = numalive(end) - numalive;

figure(1);
plot(numalive);

% plates_to_exam = [26, 100];
% nplates_to_exam = length(plates_to_exam);
% ims = zeros([imagesize, nplates_to_exam], 'uint8');
% bws = zeros([imagesize, nplates_to_exam], 'uint8');
% for i = 1:nplates_to_exam
%     iplt = plates_to_exam(i);
%     ims(:,:,i) = image_shift(imread(files(iplt).fullpath), imshifts(iplt,:));
%     bws(:,:,i) = detect_worm_2d(ims(:,:,i), minsize, maxsize, 'nogpu');
% end

% figure(2);
% for i = 1:nplates_to_exam
%     iplt = plates_to_exam(i);
%     subplot(1, nplates_to_exam, i);
%     imshow(ims(:,:,i));
%     ctds = centroids_before_exclude{iplt};
%     ctdos = centroids_origin{iplt};
%     if ~isempty(ctds)
%         hold on;
%         plot(ctds(:,1), ctds(:,2), 'r*');
%         plot(ctdos(:,1), ctdos(:,2), 'bo');
%         hold off;
%     end
% end

% figure(3);
% for i = 1:nplates_to_exam
%     iplt = plates_to_exam(i);
%     subplot(1, nplates_to_exam, i);
%     imshow(ims(:,:,i));
%     ctds = centroids_after_exclude{iplt};
%     if ~isempty(ctds)
%         hold on;
%         plot(ctds(:,1), ctds(:,2), 'r*');
%         hold off;
%     end
% end

figure(4);
for i = 1:nfiles
    imshow(image_shift(imread(files(i).fullpath), imshifts(i,:)));
    ctds = centroids_after_exclude{i};
    if ~isempty(ctds)
        hold on;
        plot(ctds(:,1), ctds(:,2), 'r*');
        hold off;
    end
    title(sprintf('%d/%d', i, nfiles));
    pause;
end
