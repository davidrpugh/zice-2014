%% outer hyperplane approximation 
% Judd, Yeltekin and Conklin (2003, 2000)
% by Markus Baldauf and Huiyu Li, 2011
% last revision: Aug 9, 2011

close all; clear all; home;
fprintf('outer hyperplane approximation \n');
tic;
% Parameters of the Prisoners Dilemma Stage game
%    c      d
% c 4 4    0 6
% d 6 0    2 2

%% parameters
    delta = 0.80;            % discount factor
    del1 = 1-delta;

    p1=[4, 0; 6, 2]; % payoff matrix
    p2=p1';
    p1max=reshape(repmat(max(p1), length(p1),1)',1,[])';
    p2max=reshape(repmat(max(p2,[],2)', length(p2),1),1,[])';

    % Payoff of player i at (a_i, a_j)
    stagepay=[reshape(p1',1,[])' reshape(p2',1,[])'];
    % best responses
    BR=[p1max p2max];

%% gradients and tangency points
    n=8; % # of gradients
    cen=[3 3]; rad=5;
    incr=360./n;
    cum=0; H=[]; Z=[];
    while cum<360
        %tangency in unit circle
        x=cosd(cum);
        y=sind(cum);
        H=[H; x y];
        Z=[Z; cen(1,1)+rad.*x cen(1,2)+rad.*y];
        cum=cum+incr;
    end
    clear x y;
    C=Z.*H*[1;1];
    L=length(H);
    G=H;                  %Use subgradient same as search directions
    
    [x,y,z]=cylinder(rad,200);
    plot(x(1,:)+cen(1,1),y(1,:)+cen(1,2), Z(:,1), Z(:,2), 'x')
    axis equal; hold on
    
%% parameters of iteration
    wmin=[-10; -10];
    iter=0; tol=1e-2; tolZ=1;
    Zold=zeros(length(Z),2);
    
while tolZ>tol
    %% optimization
    %Construct iteration
    Cla=zeros(L,4);
    Wla=zeros(2,L,4);

    for l=1:L;
        for a=1:4;
            pay=stagepay(a,:);
            options=optimset('Display', 'off');
            [Wla(:,l,a) Cla(l,a)]=linprog(-H(l,:)',[H;-eye(2)], ...
                [delta*C+del1*H*pay';-del1*BR(a,:)'-delta*wmin], ...
                [], [], [], [], [], options); 
            Cla(l,a)=-Cla(l,a);
            % if no optimum is found, then cla=-inf
            if flag<1; Cla(l,a)=-inf; end;
        end;
    end;

    [C I]=max(Cla,[],2);
    for l=1:L;
        Z(l,:)=Wla(:,l,I(l))';
    end;
    subplot(1,1,1);scatter(Z(:,1), Z(:,2));axis equal; hold on;
    wmin=min(Z)';
    
    %% convergence
    tolZ=max(max(abs(Z-Zold)./(1+abs(Zold)))); 
    %[Zround, index]=unique(round(Z.*1)./1, 'rows', 'first');
    %Z=Z(index,:);
    %tolZ=hausdorff(Z, Zold);
    if mod(iter, 5)==0
        fprintf('iteration: %d \t tolerance: %f. \n', iter, tolZ);
    end
    Zold=Z;
    iter=iter+1;
end;
fprintf('Convergence after %d iterations. \n', iter) ;

k=convhull(Z(:,1), Z(:,2));
plot(Z(k,1), Z(k,2), 'r-'); hold off
print -dpdf outer
toc;
outerpts=Z;