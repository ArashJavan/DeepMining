import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcess

sys.path.append("../../")
import sampling_utils as utils 
from gcp import GaussianCopulaProcess

### Set parameters ###
parameter_bounds = np.asarray( [[0,400]] )
nugget = 1.e-10
n_clusters = 1
cluster_evol ='constant'
corr_kernel = 'squared_exponential'
mapWithNoise= False
model_noise = None
sampling_model = 'GCP'
n_candidates= 300
n_random_init= 10
nb_GCP_steps = 9
nb_iter_final = 0
acquisition_function = 'MaxUpperBound'

window = [0,400,-0.1,1.2]
verbose = True

def scoring_function(x):
    res = (70-7*np.exp(x/50. - ((x-55.)**2)/500.) + 6*np.sin(x/40.) +3./(1.1+np.cos(x/50.)) - 15./(3.3-3*np.sin((x-70)/25.)))/100.
    return [res]


n_parameters = parameter_bounds.shape[0]
args = [corr_kernel, n_clusters,mapWithNoise,False,model_noise,nugget,1.96]
isInt = np.ones(n_parameters)

corr_kernel = args[0]
n_clusters = args[1]
GCP_mapWithNoise = args[2]
GCP_useAllNoisyY = args[3]
GCP_model_noise = args[4]
nugget = args[5]
GCP_upperBound_coef = args[6]
data_size_bounds = None

parameters = None
raw_outputs = None



fig = plt.figure()

abs = range(0,400)
f_plot = [scoring_function(i) for i in abs]
n_rows = nb_GCP_steps/3
if not(nb_GCP_steps% 3 == 0):
	n_rows += 1
#-------------------- Random initialization --------------------#

# sample n_random_init random parameters to initialize the process
init_rand_candidates = utils.sample_random_candidates_for_init(n_random_init,parameter_bounds,data_size_bounds,isInt)
for i in range(init_rand_candidates.shape[0]):
	print i
	rand_candidate = init_rand_candidates[i]
	new_output = scoring_function(rand_candidate)
	
	if(verbose):
		print('Random try '+str(rand_candidate)+', score : '+str(np.mean(new_output)))
		
	if(parameters is None):
		parameters = np.asarray([rand_candidate])
		raw_outputs = [new_output]
		mean_outputs = [np.mean(new_output)]
		std_outputs = [np.std(new_output)]
	else:
		parameters,raw_outputs,mean_outputs,std_outputs = \
			utils.add_results(parameters,raw_outputs,mean_outputs,std_outputs,rand_candidate,new_output)

X_init = parameters
Y_init = list(mean_outputs)

for i in range(nb_GCP_steps):
	rand_candidates = utils.sample_random_candidates(n_candidates,parameter_bounds,data_size_bounds,isInt)
	
	if(sampling_model == 'GCP'):
		mean_gcp = GaussianCopulaProcess(nugget = nugget,
										corr = corr_kernel,
										random_start = 5,
										n_clusters = n_clusters,
									 	mapWithNoise = GCP_mapWithNoise,
						 				useAllNoisyY = GCP_useAllNoisyY,
						 				model_noise = GCP_model_noise,
										try_optimize = True)
		mean_gcp.fit(parameters,mean_outputs,raw_outputs,obs_noise=std_outputs)

		if(acquisition_function == 'MaxUpperBound'):
			predictions,MSE,boundL,boundU = \
					mean_gcp.predict(rand_candidates,eval_MSE=True,eval_confidence_bounds=True,coef_bound = GCP_upperBound_coef)
			best_candidate_idx = np.argmax(boundU)
			best_candidate = rand_candidates[best_candidate_idx]

			idx = np.argsort(rand_candidates[:,0])
			s_candidates = rand_candidates[idx,0]
			s_boundL = boundL[idx]
			s_boundU = boundU[idx]

			ax = fig.add_subplot(n_rows,3,i+1)
			ax.plot(abs,f_plot)
			l1, = ax.plot(rand_candidates,predictions,'r+',label='GCP predictions')
			l2,= ax.plot(parameters,mean_outputs,'ro',label='GCP query points')
			l3, = ax.plot(X_init,Y_init,'bo',label='Random initialization')
			ax.fill(np.concatenate([s_candidates,s_candidates[::-1]]),np.concatenate([s_boundL,s_boundU[::-1]]),alpha=.5, fc='c', ec='None')
			ax.set_title('Step ' +str(i+1))
			ax.axis(window)

			new_output = scoring_function(best_candidate)
			l, = ax.plot(best_candidate,new_output,'yo')
			parameters,raw_outputs,mean_outputs,std_outputs = \
				utils.add_results(parameters,raw_outputs,mean_outputs,std_outputs,best_candidate,new_output)

		else:
			##EI
			predictions,MSE = \
					mean_gcp.predict(rand_candidates,eval_MSE=True,transformY=False) # we want the predictions in the GP space
			y_best = np.max(mean_outputs)
			sigma = np.sqrt(MSE)
			ei = [ utils.compute_ei((rand_candidates[j]-mean_gcp.X_mean)/mean_gcp.X_std,predictions[j],sigma[j],y_best, \
							mean_gcp.mapping,mean_gcp.mapping_derivative) \
					for j in range(rand_candidates.shape[0]) ]
			best_candidate_idx = np.argmax(ei)
			best_candidate = rand_candidates[best_candidate_idx]

			pred = mean_gcp.predict(rand_candidates,eval_MSE=False,transformY=True)
			ax = fig.add_subplot(n_rows,3,i+1)
			ax.plot(abs,f_plot)
			l1, = ax.plot(rand_candidates,pred,'r+',label='GCP predictions')
			l2, = ax.plot(parameters,mean_outputs,'ro',label='GCP query points')
			l3, = ax.plot(X_init,Y_init,'bo',label='Random initialization')
			l4, = ax.plot(rand_candidates,10.*np.asarray(ei),'g+',label='EI')
			ax.set_title('Step ' +str(i+1))
			ax.axis(window)

			new_output = scoring_function(best_candidate)
			l, = ax.plot(best_candidate,new_output,'yo')

			parameters,raw_outputs,mean_outputs,std_outputs = \
				utils.add_results(parameters,raw_outputs,mean_outputs,std_outputs,best_candidate,new_output)

	else:

		gp = GaussianProcess(theta0=.1 ,
						 thetaL = 0.001,
						 thetaU = 1.,
						 random_start = 2,
						 nugget=nugget)
		gp.fit(parameters,mean_outputs)
		print 'Theta',gp.theta_

		predictions,MSE = gp.predict(rand_candidates,eval_MSE=True)
		boundU = predictions + 1.96*np.sqrt(MSE)
		boundL = predictions - 1.96*np.sqrt(MSE)
		best_candidate_idx = np.argmax(boundU)
		best_candidate = rand_candidates[best_candidate_idx]

		idx = np.argsort(rand_candidates[:,0])
		s_candidates = rand_candidates[idx,0]
		s_boundL = boundL[idx]
		s_boundU = boundU[idx]

		ax = fig.add_subplot(n_rows,3,i+1)
		ax.plot(abs,f_plot)
		l1, = ax.plot(rand_candidates,predictions,'r+',label='GCP predictions')
		l2,= ax.plot(parameters,mean_outputs,'ro',label='GCP query points')
		l3, = ax.plot(X_init,Y_init,'bo',label='Random initialization')
		ax.fill(np.concatenate([s_candidates,s_candidates[::-1]]),np.concatenate([s_boundL,s_boundU[::-1]]),alpha=.5, fc='c', ec='None')
		ax.set_title('Step ' +str(i+1))
		ax.axis(window)

		new_output = scoring_function(best_candidate)
		l, = ax.plot(best_candidate,new_output,'yo')
		parameters,raw_outputs,mean_outputs,std_outputs = \
			utils.add_results(parameters,raw_outputs,mean_outputs,std_outputs,best_candidate,new_output)


fig.text(0.5, 0.04, 'Parameter space', ha='center')
fig.text(0.04, 0.5, 'Performance function', va='center', rotation='vertical')

if(acquisition_function == 'MaxUpperBound'):
	plt.figlegend((l,l1,l2,l3),('Next point to test','GCP predictions','GCP query points','Random initialization'),loc = 'upper center')
else:
	plt.figlegend((l,l1,l2,l3,l4),('Next point to test','GCP predictions','GCP query points','Random initialization','EI'),loc = 'upper center')

plt.show()