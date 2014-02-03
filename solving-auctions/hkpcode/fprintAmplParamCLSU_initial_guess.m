% ASMAL - A Simple MatLab/AMPL Link
% ---------------------------------
% (c) 2006 Ronald Hochreiter <ronald.hochreiter@compmath.net>
% http://www.compmath.net/ronald.hochreiter/
% 
% modifified by Che-Lin Su < c-su@kellogg.northwestern.edu >

function fprintAmplParamCLSU_initial_guess(fid, strName, dataInput, varargin)

% Initialization

vecFirstIndex = [ 1 1 1 ];
intIncrement = 1;

% First indices

intArgLen = length(varargin);
for intI = 3:-1:1
	if intArgLen >= intI
        varargin{intI};
		vecFirstIndex(intI) = varargin{intI};	
	end
end

% Analyse input data

% intType = 0;
% if iscell(dataInput)
%	intType = 4;
% elseif isscalar(dataInput)
%	intType = 1;
% elseif isvector(dataInput)
% 	intType = 2;
% else
%	intType = 3; % Admittedly, this is a bit dodgy
% end

intType = 0;
if isscalar(dataInput)
	intType = 1;
elseif isvector(dataInput)
	intType = 2;
elseif length(size(dataInput))==2
	intType = 3; % Admittedly, this is a bit dodgy
elseif length(size(dataInput))==3
	intType = 4; % Admittedly, this is a bit dodgy
end

% Type 1: Scalar

if intType == 1
	%fprintf(fid, 'param %s := %s;\n', strName, num2str(dataInput));
    fprintf(fid, 'let %s := %.16f;\n', strName, dataInput);
end

% Type 2: Vector

if intType == 2
	if ( size(dataInput, 1) > size(dataInput, 2) )
		dataInput = dataInput';
	end

	fprintf(fid, 'let %s := \n', strName);
        
	intCount = vecFirstIndex(1);
	for currentValue = dataInput
		%fprintf(fid, '\t%d\t%s\n', intCount, num2str(currentValue));
        fprintf(fid, '\t%d\t%.16f\n', intCount, currentValue);
		intCount = intCount + intIncrement;
	end

	fprintf(fid, ';\n');
end

% Type 3: Matrix

if intType == 3
	intSizeX = size(dataInput, 1);
	intSizeY = size(dataInput, 2);
        
	%fprintf(fid, 'let %s : \n', strName);
    	
	%for intI = vecFirstIndex(1):vecFirstIndex(1)+intSizeY-1
	%	fprintf(fid, '\t%d\t', intI);
	%end
	%fprintf(fid, ' := \n');
        
	for intI = vecFirstIndex(2):vecFirstIndex(2)+intSizeX-1
		%fprintf(fid, 'let %s[', strName)
		%for intJ = 1:intSizeY
		%	if (intJ == intSizeY)
		%		fprintf(fid, '%d] := ', intJ)
		%	else
		%		fprintf(fid, '%d,', intJ);
		%	end
		%end
		
		for intJ = 1:intSizeY
			fprintf(fid, 'let %s[%d,%d] := %.16f;\n', strName, intI-1, intJ, dataInput(intI, intJ));
		end
		%fprintf(fid, '\n');
	end
	%fprintf(fid, ';\n');
end

% type 4: 3-dimensional matrix

if intType == 4
	intSizeX = size(dataInput, 1);
	intSizeY = size(dataInput, 2);
    intSizeZ = size(dataInput, 3);
    
	fprintf(fid, 'let %s := \n', strName);
    for intZ = vecFirstIndex(1):vecFirstIndex(1)+intSizeZ-1    
        fprintf(fid, '[*,*,%d]: \n', intZ);     
        for intJ = vecFirstIndex(2):vecFirstIndex(1)+intSizeY-1
            fprintf(fid, '\t%d\t', intJ);
        end
        fprintf(fid, ' := \n');
        
        for intI = vecFirstIndex(3):vecFirstIndex(2)+intSizeX-1
            fprintf(fid, '%d\t', intI);
            for intJ = 1:intSizeY
                fprintf(fid, '%.16f\t', dataInput(intI, intJ, intZ));
            end
            fprintf(fid, '\n');
        end
    end
    fprintf(fid, ';\n');
end
