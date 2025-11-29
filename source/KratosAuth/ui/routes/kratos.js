const express = require('express');
const router = express.Router();
const { Configuration, FrontendApi } = require('@ory/client');
const axios = require('axios');

// Initialize Ory Kratos SDK
const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.KRATOS_PUBLIC_URL || 'http://localhost:4433',
    baseOptions: {
      withCredentials: true,
    },
  })
);

// Middleware to check if user is authenticated
async function checkAuth(req, res, next) {
  const cookie = req.header('cookie');
  
  try {
    const { data: session } = await kratos.toSession({ cookie });
    req.kratosSession = session;
    next();
  } catch (error) {
    req.kratosSession = null;
    next();
  }
}

// Home page
router.get('/', checkAuth, (req, res) => {
  if (req.kratosSession) {
    return res.redirect('/dashboard');
  }
  res.redirect('/login');
});

// Dashboard (protected)
router.get('/dashboard', checkAuth, (req, res) => {
  if (!req.kratosSession) {
    return res.redirect('/login');
  }
  
  res.render('dashboard', {
    user: req.kratosSession.identity,
  });
});

// Login page - Browser-based flow
router.get('/login', checkAuth, async (req, res) => {
  // If already logged in, redirect to dashboard
  if (req.kratosSession) {
    return res.redirect('/dashboard');
  }

  const flowId = req.query.flow;

  try {
    let flow;
    
    if (flowId) {
      // Retrieve existing flow
      const response = await kratos.getLoginFlow({
        id: flowId,
        cookie: req.header('cookie'),
      });
      flow = response.data;
    } else {
      // Create new login flow
      const response = await kratos.createBrowserLoginFlow({
        returnTo: req.query.return_to,
        cookie: req.header('cookie'),
      });
      flow = response.data;
      
      // Redirect to flow URL
      return res.redirect(`/login?flow=${flow.id}`);
    }

    res.render('login', {
      flow: flow,
      csrfToken: flow.ui.nodes.find(n => n.attributes.name === 'csrf_token')?.attributes.value,
    });
  } catch (error) {
    console.error('Login flow error:', error.response?.data || error.message);
    
    // Check if identity doesn't exist, redirect to registration
    if (error.response?.data?.error?.id === 'session_aal2_required' ||
        error.response?.status === 404) {
      return res.redirect('/registration');
    }
    
    res.render('error', {
      error: 'Failed to initialize login flow',
      details: error.response?.data || error.message,
    });
  }
});

// Submit login form
router.post('/login', async (req, res) => {
  const flowId = req.query.flow;
  const { phone, code, method, csrf_token } = req.body;

  try {
    const response = await kratos.updateLoginFlow({
      flow: flowId,
      updateLoginFlowBody: {
        method: method || 'code',
        identifier: phone,
        code: code,
        csrf_token: csrf_token,
      },
      cookie: req.header('cookie'),
    });

    // Check if verification is required
    if (response.data.continue_with) {
      const verificationAction = response.data.continue_with.find(
        action => action.action === 'show_verification_ui'
      );
      
      if (verificationAction) {
        return res.redirect(`/verification?flow=${verificationAction.flow.id}`);
      }
    }

    // Set session cookie
    if (response.headers['set-cookie']) {
      response.headers['set-cookie'].forEach(cookie => {
        res.setHeader('set-cookie', cookie);
      });
    }

    // Login successful
    res.redirect('/dashboard');
  } catch (error) {
    console.error('Login submission error:', error.response?.data || error.message);
    
    // Check if this is an unknown identity - redirect to registration
    const errorCode = error.response?.data?.ui?.messages?.[0]?.id;
    if (errorCode === 4000007 || errorCode === 4000006) {
      // Identity not found, redirect to registration with phone
      return res.redirect(`/registration?phone=${encodeURIComponent(phone)}`);
    }

    // Reload login page with error
    res.redirect(`/login?flow=${flowId}`);
  }
});

// Registration page
router.get('/registration', checkAuth, async (req, res) => {
  // If already logged in, redirect to dashboard
  if (req.kratosSession) {
    return res.redirect('/dashboard');
  }

  const flowId = req.query.flow;
  const prefilledPhone = req.query.phone;

  try {
    let flow;
    
    if (flowId) {
      // Retrieve existing flow
      const response = await kratos.getRegistrationFlow({
        id: flowId,
        cookie: req.header('cookie'),
      });
      flow = response.data;
    } else {
      // Create new registration flow
      const response = await kratos.createBrowserRegistrationFlow({
        returnTo: req.query.return_to,
        cookie: req.header('cookie'),
      });
      flow = response.data;
      
      // Redirect to flow URL with phone if provided
      const redirectUrl = `/registration?flow=${flow.id}${prefilledPhone ? `&phone=${prefilledPhone}` : ''}`;
      return res.redirect(redirectUrl);
    }

    res.render('registration', {
      flow: flow,
      prefilledPhone: prefilledPhone,
      csrfToken: flow.ui.nodes.find(n => n.attributes.name === 'csrf_token')?.attributes.value,
    });
  } catch (error) {
    console.error('Registration flow error:', error.response?.data || error.message);
    res.render('error', {
      error: 'Failed to initialize registration flow',
      details: error.response?.data || error.message,
    });
  }
});

// Submit registration form
router.post('/registration', async (req, res) => {
  const flowId = req.query.flow;
  const { phone, method, csrf_token, 'traits.phone': traitsPhone } = req.body;

  try {
    const response = await kratos.updateRegistrationFlow({
      flow: flowId,
      updateRegistrationFlowBody: {
        method: method || 'code',
        traits: {
          phone: traitsPhone || phone,
        },
        csrf_token: csrf_token,
      },
      cookie: req.header('cookie'),
    });

    // Check for continue_with actions
    if (response.data.continue_with) {
      const verificationAction = response.data.continue_with.find(
        action => action.action === 'show_verification_ui'
      );
      
      if (verificationAction) {
        return res.redirect(`/verification?flow=${verificationAction.flow.id}`);
      }
    }

    // Set session cookie
    if (response.headers['set-cookie']) {
      response.headers['set-cookie'].forEach(cookie => {
        res.setHeader('set-cookie', cookie);
      });
    }

    // Registration successful, redirect to verification
    res.redirect('/verification');
  } catch (error) {
    console.error('Registration submission error:', error.response?.data || error.message);
    res.redirect(`/registration?flow=${flowId}`);
  }
});

// Verification page
router.get('/verification', checkAuth, async (req, res) => {
  const flowId = req.query.flow;

  try {
    let flow;
    
    if (flowId) {
      // Retrieve existing flow
      const response = await kratos.getVerificationFlow({
        id: flowId,
        cookie: req.header('cookie'),
      });
      flow = response.data;
    } else {
      // Create new verification flow
      const response = await kratos.createBrowserVerificationFlow({
        returnTo: req.query.return_to,
        cookie: req.header('cookie'),
      });
      flow = response.data;
      
      return res.redirect(`/verification?flow=${flow.id}`);
    }

    res.render('verification', {
      flow: flow,
      user: req.kratosSession?.identity,
      csrfToken: flow.ui.nodes.find(n => n.attributes.name === 'csrf_token')?.attributes.value,
    });
  } catch (error) {
    console.error('Verification flow error:', error.response?.data || error.message);
    res.render('error', {
      error: 'Failed to initialize verification flow',
      details: error.response?.data || error.message,
    });
  }
});

// Submit verification form
router.post('/verification', async (req, res) => {
  const flowId = req.query.flow;
  const { code, method, csrf_token } = req.body;

  try {
    const response = await kratos.updateVerificationFlow({
      flow: flowId,
      updateVerificationFlowBody: {
        method: method || 'code',
        code: code,
        csrf_token: csrf_token,
      },
      cookie: req.header('cookie'),
    });

    // Verification successful
    res.redirect('/dashboard');
  } catch (error) {
    console.error('Verification submission error:', error.response?.data || error.message);
    res.redirect(`/verification?flow=${flowId}`);
  }
});

// Logout
router.get('/logout', async (req, res) => {
  try {
    const response = await kratos.createBrowserLogoutFlow({
      cookie: req.header('cookie'),
    });
    
    res.redirect(response.data.logout_url);
  } catch (error) {
    console.error('Logout error:', error.response?.data || error.message);
    res.redirect('/login');
  }
});

// Error page
router.get('/error', (req, res) => {
  res.render('error', {
    error: req.query.error || 'An error occurred',
    details: req.query.details || '',
  });
});

module.exports = router;
