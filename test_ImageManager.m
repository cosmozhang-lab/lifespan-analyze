digit_images = uint8(zeros(64, 64, 10));

for i = 1:10
    insert_pos = [32, 32];
    impiece = insertText(zeros(64, 64, 3), insert_pos, num2str(i-1), 'FontSize', 64, 'TextColor', [255 255 255], 'AnchorPoint', 'Center');
    digit_images(:,:,i) = impiece(:,:,1);
end

manager = ImageManager(digit_images, 2, 1);
% manager.load(8);

for i = 1:8
    gims = manager.gpu_image((0:2) + i);
    ims = gather(gims);
    for j = 1:3
%         gim = manager.gpu_image(mod(j + i - 2, 10) + 1);
%         im = gather(gim());
        im = ims(:,:,j);
        subplot(1,3,j);
        imshow(im);
    end
    manager.next();
    pause;
end