% this program was created on 2018-11-07
% to test the threshold of segmenting worms from plate background

bw = img>35;
imsz = size(bw);
imh = imsz(1);
imw = imsz(2);
bwl = bwlabel(bw);
bwp = regionprops(bwl,'area');
bwa = [bwp.Area];
bw = (bwl == find(bwa==max(bwa)));
bw = uint8(bw);
implt = img .* bw;
aplt = sum(sum(bw));
mplt = sum(sum(implt)) / aplt;
hplt = imhist(implt);
% figure;stem(1:255,hplt(2:end));

% h = hplt;
% h(h<10) = 0;
% h(1) = 0;
% th = min(h(h>0));
% while true
%     he = conv(double(h>=th), [1,-1]);
%     he = he(2:end-1);
%     if length(find(he>0)) > 1
%         break;
%     end
%     th=th+1;
% end
% hea = find(he<0);
% heb = find(he>0);
% hec = mean([hea(1),heb(2)]);
% th = hec;

% h = hplt;
% h(h<10) = 0;
% h(1) = 0;
% hea = find(h>0);
% hea = hea(end);
% hem = find(h==max(h));
% hem = hem(1);
% heb = hem-(hea-hem);
% th = heb;

th = 90;

bwwrm = (implt<th);
se = strel('disk',5);
bwwrm = imopen(bwwrm,se);
% bwwrm = imclose(bwwrm,se);
bwlwrm = bwlabel(bwwrm);
bwp = regionprops(bwwrm,'Area');
bwa = [bwp.Area];
ibw = find((bwa>500)&(bwa<3500));
bwlwrm2 = zeros(size(bwwrm),'int32');
for i = 1:length(ibw)
    bwlwrm2 = bwlwrm2 + int32(bwlwrm==ibw(i))*i;
end
% figure; imshow(bwlwrm2>0);

figure; imshow(implt);

coorx = repmat(1:imw,[imh,1]);
coory = repmat(1:imh,[imw,1])';
for i = 1:max(max(bwlwrm2))
    regi = (bwlwrm2==i);
    regl = min(coorx(regi));
    regr = max(coorx(regi));
    regt = min(coory(regi));
    regb = max(coory(regi));
    rectangle('Position',[regl,regt,regr-regl+1,regb-regt+1],'EdgeColor','r');
end


