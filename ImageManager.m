classdef ImageManager < handle
    %IMAGES_MANAGER 此处显示有关此类的摘要
    %   此处显示详细说明
    
    properties(SetAccess = private)
        backward_buffer_size;
        forward_buffer_size;
        gpu_buffer;
        images;
        curridx;
        imsize;
        m_gpu_coors;
    end
    
    methods
        function obj = ImageManager(data, forward_buffer_size, backward_buffer_size)
            if nargin < 3
                backward_buffer_size = 0;
            end
            if nargin < 2
                forward_buffer_size = 0;
            end
            obj.images = data;
            obj.imsize = [size(data,1), size(data,2)];
            obj.forward_buffer_size = forward_buffer_size;
            obj.backward_buffer_size = backward_buffer_size;
            buffer_size = backward_buffer_size + forward_buffer_size + 1;
            obj.gpu_buffer = gpuArray(zeros([size(data,1), size(data,2), buffer_size], class(data)));
            obj.m_gpu_coors = [];
            obj.init();
        end
        
        function [buffidx] = buff_index(obj, image_idx)
            buffer_size = obj.backward_buffer_size + obj.forward_buffer_size + 1;
            image_count = size(obj.images, 3);
            buffidx = mod(mod(image_idx - 1, image_count) + obj.backward_buffer_size, buffer_size) + 1;
        end
        
        function [out] = size(obj, idim)
            if nargin < 2
                out = obj.imsize;
            else
                out = obj.imsize(idim);
            end
        end
        
        function [] = init(obj)
            image_count = size(obj.images, 3);
            new_indexes = mod(((-obj.backward_buffer_size):(obj.forward_buffer_size)), image_count) + 1;
            counter = 0;
            for idx = new_indexes
                obj.gpu_buffer(:, :, obj.buff_index(idx)) = obj.images(:, :, idx);
                counter = counter + 1;
            end
            obj.curridx = 1;
        end
        
        function [] = load(obj, image_idx)
            image_count = size(obj.images, 3);
            image_idx = mod(image_idx - 1, image_count) + 1;
            curr_indexes = mod(((-obj.backward_buffer_size):(obj.forward_buffer_size)) + obj.curridx - 1, image_count) + 1;
            curr_indexes = curr_indexes((curr_indexes <= image_count) & (curr_indexes >= 1));
            new_indexes = mod(((-obj.backward_buffer_size):(obj.forward_buffer_size)) + image_idx - 1, image_count) + 1;
            new_indexes = new_indexes((new_indexes <= image_count) & (new_indexes >= 1));
            counter = 0;
            for idx = new_indexes
                if isempty(find(curr_indexes == idx, 1))
                    obj.gpu_buffer(:, :, obj.buff_index(idx)) = obj.images(:, :, idx);
                    counter = counter + 1;
                end
            end
            obj.curridx = image_idx;
            % fprintf('Manager loaded %d images\n', counter);
        end
        
        function [] = next(obj)
            obj.load(obj.curridx + 1);
        end
        function [] = previous(obj)
            obj.load(obj.curridx - 1);
        end
        
        function [out] = gpu_image(obj, image_indexes)
            image_count = size(obj.images, 3);
            curr_indexes = mod(((-obj.backward_buffer_size):(obj.forward_buffer_size)) + obj.curridx - 1, image_count) + 1;
            curr_indexes = curr_indexes((curr_indexes <= image_count) & (curr_indexes >= 1));
            for i = 1:length(image_indexes)
                if isempty(find(curr_indexes == image_indexes(i), 1))
                    throw('Image is not loaded yet');
                end
            end
            out = obj.gpu_buffer(:, :, obj.buff_index(image_indexes));
        end
        
        function [out] = image(obj, image_idx)
            out = obj.images(:, :, image_idx);
        end
        
        function [out] = gpu_coors(obj)
            if isempty(obj.m_gpu_coors)
                obj.m_gpu_coors = gpuArray(make_coors(obj.size));
            end
            out = obj.m_gpu_coors;
        end
    end
    
end

