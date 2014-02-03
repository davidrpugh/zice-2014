% © Timothy P. Hubbard
% timothy.hubbard@colby.edu

% CDFs that cross once---create second CDF using piecewise polynomials

function [breaks,coefs,nparts,ncoefs,d] = genpiecewiseCDFs_onecross( ...
	vlow,vhigh,zz)


% CDF values of second (piecewise) distribution
x = [0 1/6 1/3 1/2 2/3 5/6 1];
y = [0 1/9 1/4 1/2 9/12 16/18 1];

% valuations at which two cdfs are equal
%fprintf('CDFs cross at v = %.16f\n\n',1/2)

v = linspace(vlow,vhigh,1000000);

% second distribution is piecewise cubic polynomials
pp = spline(x,y);
[breaks,coefs,nparts,ncoefs,d] = unmkpp(pp);

% construct polynomial from pieces
Fv = zeros(nparts,length(v));
fv = zeros(nparts,length(v));
for i=2:nparts+1
	for j=1:ncoefs
		% cdf
		Fv(i-1,:) = coefs(i-1,j)*(v - breaks(i-1)).^(ncoefs - j) + ...
			Fv(i-1,:);
		% pdf
		fv(i-1,:) = (ncoefs - j)*coefs(i-1,j)* ...
			(v - breaks(i-1)).^(ncoefs - j - 1) + fv(i-1,:);
	end
end

% pick which pieces are correct and assemble crossing cdf
Fcross = [];
fcross = [];
for i=2:nparts+1
	inds = find(v >= breaks(i-1) & v < breaks(i));
	if (i == nparts+1)
		inds = [inds length(v)];
    end
	Fcross = [Fcross Fv(i-1,inds)];
	fcross = [fcross fv(i-1,inds)];
end

% some checks
minFcross = min(Fcross);
maxFcross = max(Fcross);
minfcross = min(fcross);
maxfcross = max(fcross);
% see if CDF goes from 0 to 1
if (minFcross ~= 0) || (maxFcross ~= 1)
	fprintf('Not proper CDF\n')
end
% make sure CDFs are monotonic
if (issorted(Fcross) == 0)
	fprintf('One of the distributions is not monotonic\n')
end

if strcmpi(zz,'plot')
	Fbase = v;
	Fratio = Fbase./Fcross;
	plot(v,Fratio,'-.')
end
	