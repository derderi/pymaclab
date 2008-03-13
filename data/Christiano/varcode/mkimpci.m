function [cil,ciu,varimpneg,varimppos,varz]=mkimpci(beta,a0,nlags,errshk,nstep,ndraws,nobs,pctg,resid,sigma,numtries,mkmatrix,mkstart,varargin)
% MKIMPCI calculates confidence intervals for impulse response functions.
% Syntax [cil,ciu,varimpneg,varimppos,varz]=mkimpci(beta,a0,hascon,ndraws,nobs,nstep,errshk,errshk,pctg,nonrec,resid)
% CIL 100*pct  percentile of the point estimates  CIU 100*(1-pct) percentile of the sample
% VARIMPNEG - Estimated Impulse - 2*STD Dev VARIMPPOS Estimated Impulse + 2*Std Dev VARZ = Sample Variance
% Creates Monte Carlo (Bootstrap) confidence intervals 
% Generates 2*nobs observations of Data 
% using Y = beta*Ylag + inv(a0)*ut where ut is i.i.d standard Normal
% Estimates a var on the last nobs observations 
% Uses the VAR estimate to generate impulse responses 
% Repeats ndraws times
% Calculates the sample variance for each point estimate.
% Returns Impvar which is the estimated impulse response function
% + or - 2 *standard Errors
% This samples from the residuals if residuals are given
% NOTE The starting values are always set equal to zero. I however
% through away the first nobs of data so it should not matter.

beta = beta';
a0inv = inv(a0);
nvars = length(a0);
hascon = size(beta,1)-nvars*nlags;

ydata = zeros(2*nobs,nvars);
zlag = zeros(1,nvars*nlags);
erz = zeros(2*nobs,nvars);

for icnt=1:ndraws;
   disp(['Now doing trial ' num2str(icnt)])
   %loop over the number of draws
   % generate data and estimate the var
   % and then calculate impulse response functions
   
   % step 1 generate the data
   if nargin > 8
      if ~isempty(resid);
         %if we have the residuals we can bootstrap off the residuals
         erz = resid(ceil(size(resid,1)*rand(2*nobs,1)),:);
         %I generate a random number bounded between 0 and # of residuals
         %I then use the ceil function to select that row of the residuals
         %this is equivalent to sampling with replacement.    
      else;
         %otherwise we can use monte carlo methods    
         u=randn(2*nobs,nvars); % create the fundamental error terms N(0,1)     
         for jj=1:2*nobs;         
            erz(jj,:)=(a0inv*u(jj,:)')';       
            %create the VAR error terms    
         end; 
      end;
 else
      %otherwise we can use monte carlo methods
      
      u=randn(2*nobs,nvars); % create the fundamental error terms N(0,1)
      for jj=1:2*nobs;

         erz(jj,:)=(a0inv*u(jj,:)')';
         %create the VAR error terms       
      end;
      
   end;
   
   
   %we will add in the constant term to the residual
   %it makes the calculations easier ahead.
   for kk=1:nvars;
 	   erz(:,kk)=erz(:,kk)+hascon*beta(1,kk);
       %create the VAR error terms plus a constant if included
   end;

   
   % intialize the first observations
   zlag=[];
   for k=1:nlags
      ydata(k,:)=erz(k,:);
      zlag = [ydata(k,:) zlag]; 
   end;
   
   for jj=nlags+1:2*nobs;
   	ydata(jj,:)=erz(jj,:)+zlag*beta(hascon+1:size(beta,1),:);
   	zlag=[ydata(jj,:) zlag(1,1:(nlags-1)*nvars)];
	end;
   
   %estimate var and calculate a0 matrix on simulated data
   %I throw away the first nobs of data as I want to avoid any starting value 
   %problems
   [best,sigest]=estimatevar(ydata(1*nobs+1:end,:),nlags,hascon);
   
   if nargin > 9
      disp('Estimating Nonrecursive Azero matrix')
      a0est=estnonreca(sigma,numtries,mkmatrix,mkstart,varargin{:});;
   else
      a0est=inv(chol(sigest)');
   end;
      
      
    %calculate impulse responses
   impz=mkimprep(best,a0est,nlags,errshk,nstep);
   %if you don't have three dimensional arrays this will break.
   cnfdints(:,:,icnt)=impz;
   %save them and do it again
   
   
end;

%find the upper and lower bounds. 
cnfsrt= sort(cnfdints,3);
cil = squeeze(cnfsrt(:,:,round(pctg*ndraws)));
ciu = squeeze(cnfsrt(:,:,round((1-pctg)*ndraws)));


for zx=1:nvars;
   for zy=1:nstep;
      cnfdints(zy,zx,:) = cnfdints(zy,zx,:)-mean(cnfdints(zy,zx,:),3);
   end;
end;

trimpz=mkimprep(beta',a0,nlags,errshk,nstep);

varz = (1/ndraws)*sum(cnfdints.^2,3);
varimppos = trimpz + 2*sqrt(varz);
varimpneg = trimpz - 2*sqrt(varz);



%end of procedure

