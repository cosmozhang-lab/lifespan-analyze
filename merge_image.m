function [ outim ] = merge_image( varargin )

datacls = '';
outim = [];

for i = 1:length(varargin)
    single = varargin{i};
    if ~isempty(single)
        if isempty(outim)
            outim = zeros(size(single, 1), size(single, 2), length(varargin));
        end
        if isempty(datacls)
            datacls = class(single);
        end
        outim(:,:,i) = single;
    end
end

outim = cast(outim, datacls);

end

