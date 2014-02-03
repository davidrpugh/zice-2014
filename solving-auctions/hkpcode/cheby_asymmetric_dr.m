% © Timothy P. Hubbard
% timothy.hubbard@colby.edu

% approximate bid function at first-price, sealed-bid auction. inverse bid
% function is approximated by a Chebyshev polynomial, the coefficients of
% which are found using AMPL (with SNOPT solver) 

clear all
clc

% put useguess = 1 to use a guess from a previous solution; otherwise,
% useguess = 0 does not use a prior solution's output as an initial guess
useguess = 0;

% select case to consider: piecewise1 or piecewise
dists = 'piecewise1';

% number of players
p = 2;

% support
vlow = 0;
vhigh = 1;

% if want to save solutions to file: 0 is off, 1 is on
savesoln = 0;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% define parameters of instance
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% degree of each Chebyshev polynomial
d = 3;

if strcmpi(dists,'piecewise1')
	[breaks,coefs,nparts,ncoefs,dim] = genpiecewiseCDFs_onecross(vlow, ...
		vhigh,'noplot');
elseif strcmpi(dists,'piecewise2')
	[breaks,coefs,nparts,ncoefs,dim] = genpiecewiseCDFs_twocross(vlow, ...
		vhigh,'noplot');
else
    fprintf('Case does not exist; set value on line 14 to piecewise1 or piecewise2.')
end

% number of points in grid space
npts = 60;
% number of points to uses on shape constraints
nconpts = 100;

% parameters for figure properties
lwidth = 2;
fsize = 14;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% export data to AMPL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fid = fopen('fpsb.dat', 'w');
fprintf(fid,'# © Timothy P. Hubbard\n');
fprintf(fid,'# timothy.hubbard@colby.edu\n\n');
fprintf(fid,'# parameter data file\n');
fprintf(fid,'# values output: %s\n\n',datestr(now));
fprintf(fid,'data;\n\n');
fprintAmplParamCLSU(fid,'d',d);
fprintAmplParamCLSU(fid,'p',p);
fprintAmplParamCLSU(fid,'npts',npts);
fprintAmplParamCLSU(fid,'nconpts',nconpts);
fprintAmplParamCLSU(fid,'pi',pi);
fprintAmplParamCLSU(fid,'vlow',vlow);
fprintAmplParamCLSU(fid,'vhigh',vhigh);
fprintAmplParamCLSU(fid,'breaks',breaks);
fprintAmplParamCLSU(fid,'coefs',coefs);
fprintAmplParamCLSU(fid,'nparts',nparts);
if (useguess == 1) || (d > 3)
    fpsbsoln;
    fprintAmplParamCLSU_initial_guess(fid,'bhigh',bhigh);
    fprintAmplParamCLSU_initial_guess(fid,'a',a);
end
fclose(fid);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% call AMPL from Matlab
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!myampl fpsb_piecewise.dr	
fpsbsoln;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% evaluate solution and plot
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% points to evaluate (inverse) bid function at
u = linspace(vlow,bhigh,10000);
z = 2*(u - vlow)./(bhigh - vlow) - 1;
T = evalchebypoly(z,d);

set(0,'defaulttextinterpreter','latex','Defaulttextfontsize',fsize);

% construct Chebyshev polynomial approximation
for j=1:p
	for i=1:length(u)
		aT(:,i) = a(:,j).*T(:,i);
	end
	fhat(:,j) = sum(aT);
end
figure
set(gcf,'DefaultLineLineWidth',lwidth)
set(gca,'FontSize',fsize)
plot(fhat(:,1),u,fhat(:,2),u,'-.',[0 vhigh],[0 vhigh])
xlabel('$\mathbf{v}$')
ylabel('$\mathbf{s}$')
axis([vlow vhigh vlow vhigh])
L = legend('$\mathbf{\hat{\varphi}_1(s)}$', ...
    '$\mathbf{\hat{\varphi}_2(s)}$');
set(L,'Interpreter','latex','Location','NorthWest')


% compute ratios of interest
figure 
set(gcf,'DefaultLineLineWidth',lwidth)
set(gca,'FontSize',fsize)
hold all
% set restrict = 1 to restrict plot to an area like in paper; set restrict
% = 0 to have an unrestricted plot of entire ratios
restrict = 0;
if strcmpi(dists,'piecewise1')
	genpiecewiseCDFs_onecross(vlow,vhigh,'plot');
	[Epayoff,vEpayoff] = calcexppayoff(a,bhigh,d,vlow,vhigh,breaks, ...
		coefs,nparts,ncoefs,restrict,dists);
elseif strcmpi(dists,'piecewise2')
	genpiecewiseCDFs_twocross(vlow,vhigh,'plot');
	[Epayoff,vEpayoff] = calcexppayoff(a,bhigh,d,vlow,vhigh,breaks, ...
		coefs,nparts,ncoefs,restrict,dists);
end
box on