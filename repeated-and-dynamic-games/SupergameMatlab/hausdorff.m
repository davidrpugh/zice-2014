function [distance] = hausdorff(A, B)

% hausdorff distance
% starting from Zold
temp1=repmat(permute(B, [3 1 2]), length(A),1);
temp2=repmat(permute(A, [1 3 2]), 1, length(B));
D1=min(sqrt(sum((temp1-temp2).^2,3)))';

% starting from Z
temp1=repmat(permute(A, [3 1 2]), length(B),1);
temp2=repmat(permute(B, [1 3 2]), 1, length(A));
D2=min(sqrt(sum((temp1-temp2).^2,3)))';
distance=max([D1; D2]);
