% © Timothy P. Hubbard
% timothy.hubbard@colby.edu

% calculate expected payoffs given approximated bid functions

function [Epayoff,vuse] = calcexppayoff(a,bhigh,d,vlow,vhigh,breaks, ...
	coefs,nparts,ncoefs,restrict,dists)

p = 2;
b = linspace(vlow,bhigh,10000);

z = 2*(b - vlow)./(bhigh - vlow) - 1;
T = evalchebypoly(z,d);

% construct Chebyshev polynomial approximation
for j=1:p
	for i=1:length(b)
		aT(:,i) = a(:,j).*T(:,i);
	end
	fhat(:,j) = sum(aT);
end
v = fhat';
v1 = v(1,:);
v2 = v(2,:);

% we need the valuations that the expected payoffs are evaluated at to be
% the same, so I interpolate the bids that correspond with the chosen
% valuations
vuse = linspace(vlow,vhigh,1000);
buse1 = interp1(v1,b,vuse);
buse2 = interp1(v2,b,vuse);

% compute rival's valuation that would correspond with the bid implied by
% each player's valuation
z1 = 2*(buse1 - vlow)./(bhigh - vlow) - 1;
T1 = evalchebypoly(z1,d);
z2 = 2*(buse2 - vlow)./(bhigh - vlow) - 1;
T2 = evalchebypoly(z2,d);
% construct Chebyshev polynomial approximation
for j=1:p
	for i=1:length(buse1)
		aT1(:,i) = a(:,j).*T1(:,i);
		aT2(:,i) = a(:,j).*T2(:,i);
	end
	fhat1(:,j) = sum(aT1);
	fhat2(:,j) = sum(aT2);
end
vother1 = fhat1';
vother2 = fhat2';
vofrivalfor1 = vother1(2,:);
vofrivalfor2 = vother2(1,:);


% evaluate CDFs at valuations of rivals
Fbase = vofrivalfor2;
% construct polynomial from pieces
Fv = zeros(nparts,length(vofrivalfor1));
for i=2:nparts+1
	for j=1:ncoefs
		% cdf
		Fv(i-1,:) = coefs(i-1,j)*(vofrivalfor1 - breaks(i-1)).^(ncoefs - j) + ...
			Fv(i-1,:);
	end
end

% pick which pieces are correct and assemble crossing cdf
Fcross = [];
for i=2:nparts+1
	inds = find(vofrivalfor1 >= breaks(i-1) & vofrivalfor1 < breaks(i));
	% if, because of approximation, the find command misses initial
	% elements that are relevant for first piece of polynomial, this
	% informs it manually
	if (i == 2) && (min(inds) > 1)
		inds = [1:1:(min(inds)-1) inds];
	end
	% add to last part the highest element if necessary---rival's implied
	% valuation may be less than highest bid in which case unnecessary
	if (i == nparts+1) && ...
			(length(Fcross) + length(inds) ~= length(vofrivalfor1))
		inds = [inds length(vofrivalfor1)];
	end
	Fcross = [Fcross Fv(i-1,inds)];
end


% calculate expected payoffs
for i=1:2
	if i == 1
		Epayoff(i,:) = (vuse - buse1).*Fcross;
	elseif i == 2
		Epayoff(i,:) = (vuse - buse2).*Fbase;
	end
end
% check if valuations near zero involve negative payoff and make positive
% if value is less than 1e-12...this is a technicality to avoid vertical
% line at 0 in plot
neginds = find(Epayoff < 0);
for i=1:length(neginds)
	if abs(Epayoff(neginds)) < 1e-12
		if neginds(i) > 1
			Epayoff(neginds(i)) = abs(Epayoff(neginds(i)));
		else
			Epayoff(neginds(i)) = 0;
		end
	end
end


% plot endogenous ratio
hold all
Rratio = Epayoff(2,:)./Epayoff(1,:);
plot(vuse,Rratio,'--',vuse,ones(size(vuse)))
[L,Obj] = legend('$\mathbf{P_{2,1}(v)}$','$\mathbf{\hat{R}_{2,1}(v)}$');
if (restrict == 1) && strcmpi(dists,'piecewise2')
	xlim([.2 1])
elseif strcmpi(dists,'piecewise2')
	xlim([vlow vhigh])
	ylim([0 7])
elseif (restrict == 1) && strcmpi(dists,'piecewise1')
	xlim([vlow vhigh])
	ylim([.6 1.6])
elseif strcmpi(dists,'piecewise1')
	xlim([vlow vhigh])
end
xlabel('$\mathbf{v}$')

set(L,'Interpreter','latex')
