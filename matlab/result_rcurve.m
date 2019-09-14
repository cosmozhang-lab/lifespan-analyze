function [ rcurve, rctds, rcnts ] = result_rcurve( centroids, rvalues )
% result_rcurve: Registrate worms in all frames and withdraw a time-rvalue
% curve for each worm.
% PARAMS:
%     centroids: 1*T cell, each corresponds to one frame and is a Nt*2
%                matrix, which corresponds to the centroids of Nt worms.
%     rvalues:   1*T cell, each corresponds to one frame and is a Nt*1
%                matrix, which corresponds to the rvalues of Nt worms.
% RETURN:
%     rcurve:    N*T matrix, each row is the time-rvalue curve of one of
%                the N worms.
%     rctds:     N*2 matrix, each row is the centroid of one of the N worms.
%     rcnts:     N*1 vector, each element is the count of frames in which
%                this worm appears.

nfiles = length(centroids);
rcurve = nan(32, nfiles);
rctds = nan(32, 2);
rcnts = zeros(32, 1);
rn = 0;
for i = 1:nfiles
    ctds = centroids{i};
    rds = rvalues{i};
    for j = 1:size(ctds,1)
        if isnan(rds(j)) || rds(j) < 0.1; continue; end
        if rn == 0
            rctds(1,:) = ctds(j,:);
            rcurve(1,i) = rds(j);
            rcnts(1) = 1;
            rn = 1;
            continue;
        end
        dists = sqrt(sum((repmat(ctds(j,:), [rn,1]) - rctds(1:rn,:)) .^ 2, 2));
        [~,k] = min(dists);
        if dists(k) < 150
        	rcurve(k,i) = rds(j);
            rctds(k,:) = (rctds(k,:) * rcnts(k) + ctds(j,:)) / (rcnts(k) + 1);
            rcnts(k) = rcnts(k) + 1;
        else
            if rn == size(rcurve, 1)
                rcurve = [rcurve;nan(size(rcurve))];
                rctds = [rctds;nan(size(rctds))];
                rcnts = [rcnts;zeros(size(rcnts))];
            end
            rn = rn + 1;
            rcurve(rn, i) = rds(j);
            rctds(rn, :) = ctds(j,:);
            rcnts(rn) = 1;
        end
    end
end

rcurve = rcurve(1:rn, :);
rctds = rctds(1:rn, :);
rcnts = rcnts(1:rn, :);

end

