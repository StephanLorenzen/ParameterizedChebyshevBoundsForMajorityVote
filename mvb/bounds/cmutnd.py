#
# Implements the MU bound.
#
import numpy as np
from math import log, sqrt, exp
from .tools import solve_kl_sup, solve_kl_inf
from ..util import warn, kl, uniform_distribution, random_distribution, softmax, GD, RProp, iRProp 

# Calculate the CCTND bound
def MU(tandem_risk, gibbs_risk, n, n2, KL, mu_opt = 0., delta=0.05):
    #calculate the bound for a given mu
    def _bound(mu):
        # UpperBound_TandemRisk by inverse kl
        rhs_tr = ( 2.0*KL + log(4.0*sqrt(n2)/delta) ) / n2
        ub_tr  = solve_kl_sup(tandem_risk, rhs_tr)
        
        if mu>=0:
            # LowerBound_GibbsRisk by inverse kl
            rhs_gr = ( KL + log(4.0*sqrt(n)/delta) ) / n
            eb_gr  = solve_kl_inf(gibbs_risk, rhs_gr)
        else:
            # UpperBound_GibbsRisk by inverse kl
            rhs_gr = ( KL + log(4.0*sqrt(n)/delta) ) / n
            eb_gr  = solve_kl_sup(gibbs_risk, rhs_gr)

        # bound
        muTandemUB = ub_tr - 2*mu*eb_gr + mu**2
        bnd = muTandemUB / (0.5-mu)**2
        return (bnd, mu, ub_tr, eb_gr, muTandemUB)
    
    opt_bnd, opt_mu, opt_ub_tr, opt_eb_gr, opt_muTandemUB = _bound(mu=mu_opt)

    return (min(1.0, opt_bnd), (opt_mu,) , min(1.0, opt_ub_tr), min(1.0, opt_eb_gr), min(1.0, opt_muTandemUB))

# Optimize over CCTND bound
# options = {'optimizer':<opt>, 'max_iterations':<iter>, 'eps':<eps>, 'learning_rate':<lr>}
#
# Default for opt is iRProp
def optimizeMU(tandem_risks, gibbs_risks, n, n2, delta=0.05, abc_pi=None, options=None):
    options = dict() if options is None else options
    
    def _bound(mu): 
        return _optimizeMU(tandem_risks, gibbs_risks, n, n2, mu=mu, delta=delta, abc_pi=abc_pi, options=options)

    opt_bnd, opt_rho, opt_mu, opt_lam, opt_gam = _bound(mu=None)

    return (min(opt_bnd, 1.0), opt_rho, opt_mu, opt_lam, opt_gam)

# Same as above, but mu is now a single value. If None, mu will be optimized
def _optimizeMU(tandem_risks, gibbs_risks, n, n2, mu=None, delta=0.05, abc_pi=None, options=None):
    options = dict() if options is None else options
    optimizer = options.get('optimizer', 'iRProp')
    mu_input = mu

    if optimizer not in ['GD', 'RProp', 'iRProp']:
        warn('optimizeMU: unknown optimizer: \''+optimizer+'\', using iRProp')
        optimizer = 'iRProp'

    def _gr(rho): # Compute Gibbs risk from gibbs_risk list and rho
        return np.average(gibbs_risks, weights=rho)
    def _tnd(rho): # Compute Tandem risk from tandem_risk matrix and rho
        return np.average(np.average(tandem_risks, weights=rho, axis=0), weights=rho)
    def _bound(rho, mu=None, lam=None, gam=None, pm=None): # Compute bound
        rho = softmax(rho)
        gr  = _gr(rho)
        tnd = _tnd(rho)
        KL  = kl(rho,pi)
        
        # upper bound of tnd loss
        if lam is None:
            lam = 2.0 / (sqrt((2.0*n2*tnd)/(2*KL+log(4.0*sqrt(n2)/delta)) + 1) + 1)
        ub_tnd = tnd/(1-lam/2)+(2*KL+log(4*sqrt(n2)/delta))/(lam*(1-lam/2)*n2)
        
        # empirical bound of Gibbs loss
        if (mu is not None and mu>=0) or pm=='plus':
            # take the lower bound
            if gam is None:
                gam = min(2.0, sqrt( (2.0*KL+log(16.0*n/delta**2)) / (n*gr) ))
            eb_gr = max(0.0, (1-gam/2.0)*gr-(KL+log(4*sqrt(n)/delta))/(gam*n))
        elif (mu is not None and mu<0) or pm=='minus':
            # take the upper bound
            if gam is None:
                gam = 2.0 / (sqrt((2.0*n*gr)/(KL+log(4.0*sqrt(n)/delta)) + 1) + 1)
            eb_gr = gr/(1-gam/2)+(KL+log(4*sqrt(n)/delta))/(gam*(1-gam/2)*n)
        else:
            warn('something went wrong')
        
        ### optimize using the mu from the previous round
        nmu  = (0.5*eb_gr - ub_tnd)/(0.5-eb_gr)
        bound  = (ub_tnd - 2*mu*eb_gr + mu**2) / (0.5-mu)**2
        return (bound, nmu, lam, gam)
        
        
        """
        ### using f+ and f-
        if mu is None:
            mu = (0.5*eb_gr - ub_tnd)/(0.5-eb_gr)
        if pm == 'plus':
            mu = max(0.0, mu)
        elif pm == 'minus':
            mu = min(-1e-9, mu)
        bound  = (ub_tnd - 2*mu*eb_gr + mu**2) / (0.5-mu)**2

        return (bound, mu, lam, gam)
        """

    def _gradient(rho, mu, lam, gam):
        if mu >= 0:
            a = 1.0/(1.0-lam/2.0)
            b = mu*(1-gam/2.0)
            c = 1.0/(lam*(1.0-lam/2.0)*n2) + mu/(gam*n)
        else:
            a = 1.0/(1.0-lam/2.0)
            b = mu/(1.0-gam/2.0)
            c = 1.0/(lam*(1.0-lam/2.0)*n2) - mu/(gam*(1.0-gam/2.0)*n)
            
            
        Srho = softmax(rho)
        # D_jS_i = S_i(1[i==j]-S_j)
        Smat = -np.outer(Srho, Srho)
        np.fill_diagonal(Smat, np.multiply(Srho,1.0-Srho))

        return 2*np.dot(a*np.dot(tandem_risks, Srho)-b*gibbs_risks+c*(1+np.log(Srho/pi)), Smat)
        
    max_iterations = options.get('max_iterations', None)
    eps = options.get('eps', 10**-9)
        
    if optimizer=='GD':
        def _optRho(rho, mu, lam, gam):
            lr = options.get('learning_rate', 1)
            return GD(lambda x: _gradient(x,mu,lam,gam), lambda x: _bound(x,mu,lam,gam)[0], rho,\
                    max_iterations=max_iterations, lr=lr, eps=eps)
    elif optimizer=='RProp':
        max_iterations = options.get('max_iterations', 1000)
        def _optRho(rho, mu, lam, gam):
            return RProp(lambda x: _gradient(x,mu,lam,gam),rho,eps=eps,max_iterations=max_iterations)
    elif optimizer=='iRProp':
        max_iterations = options.get('max_iterations', 100)
        def _optRho(rho, mu, lam, gam):
            #print('optimize optrho')
            return iRProp(lambda x: _gradient(x,mu,lam,gam), lambda x: _bound(x,mu,lam,gam)[0], rho,\
                    eps=eps,max_iterations=max_iterations)
    
    ### optimize use mu from the previous round
    m = gibbs_risks.shape[0]
    pi  = uniform_distribution(m) if abc_pi is None else np.copy(abc_pi)
    rho = uniform_distribution(m) if abc_pi is None else np.copy(abc_pi)
    mu = 0.

    b, nmu, lam, gam  = _bound(rho, mu=mu)
    bp = b+1
    while abs(b-bp) > eps:
        bp = b
        # Optimize rho
        nrho = _optRho(rho,mu,lam,gam)
        
        rho, mu = nrho, nmu
        # Optimize lam, gam, mu
        b, nmu, lam, gam = _bound(rho, mu=mu)
        if b > bp:
            b = bp
            break
        #rho, mu, lam, gam = nrho, nmu, nlam, ngam
    
    return (b, softmax(rho), mu, lam, gam)
    
    """
    b, mu, lam, gam  = _bound(rho, mu=init_mu)
    bp = b+1
    while abs(b-bp) > eps:
        bp = b
        # Optimize rho
        nrho = _optRho(rho,mu,lam,gam)
        # Optimize lam + gam ( also mu if mu_input is None; otherwise, mu is fixed to be mu_input)
        b, nmu, nlam, ngam = _bound(nrho, mu=mu)
        if b > bp:
            b = bp
            break
        rho, mu, lam, gam = nrho, nmu, nlam, ngam
    
    return (b, softmax(rho), mu, lam, gam)
    """
    
    """
    ### initialize with f_0
    ### then optimize using f+ and f-
    ### choose the best of these three
    def f_half(mu_input=None, pm=None, rho_init=None): #pm = 'plus' or 'minus'
        rho = uniform_distribution(m) if rho_init is None else rho_init
        b, mu, lam, gam  = _bound(rho, mu=mu_input, pm=pm)
        bp = b+1
        while abs(b-bp) > eps:
            bp = b
            # Optimize rho
            nrho = _optRho(rho,mu,lam,gam)
            # Optimize lam + gam ( also mu if the mu_input is None; otherwise, mu is fixed to be mu_input)
            b, nmu, nlam, ngam = _bound(nrho, mu=mu_input, pm=pm)
            if b > bp:
                b = bp
                break
            rho, mu, lam, gam = nrho, nmu, nlam, ngam
        return (b, softmax(rho), mu, lam, gam)
    
    m = gibbs_risks.shape[0]
    pi = uniform_distribution(m)
    
    f_0 = f_half(mu_input=0.)
    f_plus = f_half(mu_input=None, pm='plus', rho_init=f_0[1])
    f_minus = f_half(mu_input=None, pm='minus', rho_init=f_0[1])
    
    opt_f = f_0
    if f_plus[0] <  opt_f[0]:
        opt_f = f_plus
    if f_minus[0] < opt_f[0]:
        opt_f = f_minus
    return opt_f
    """
    