% © Timothy P. Hubbard
% timothy.hubbard@colby.edu

% define recursively the Chebyshev polynomials (of the first kind)

function T = evalchebypoly(z,n)

m = length(z);

T = ones(1,m);
T = [T; z];
for i=3:n+1
	T(i,:) = 2*z.*T(i-1,:) - T(i-2,:);
end

% alternative way of building Chebyshev polynomials
%Torig = T;
%for i=1:n+1
%	T(i,:) = cos((i - 1)*acos(z));
%end
%T - Torig

% plot Chebyshev polynomials (for fun)
%figure
%hold all
%for i=1:n+1
%	plot(z,T(i,:))
%end
%axis tight