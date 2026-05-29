/**
 * Supabase auth for AI Engineering from Scratch.
 * Handles GitHub OAuth sign-in/out and exposes window.AIFSAuth.
 * Depends on: supabase-js CDN (window.supabase), progress.js (window.AIFSProgress)
 * ref: site/auth.js
 */
(function () {
  var SUPABASE_URL = 'https://kewzyxvxsgdekykcedut.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_smxgRX90dnkFZXJDqX8L8g_fnTC7t_0';

  var client = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
  var authListeners = [];
  var currentUser = null;

  function notifyListeners() {
    for (var i = 0; i < authListeners.length; i++) {
      try { authListeners[i](currentUser); } catch (_) {}
    }
  }

  // Check for an existing session on page load (handles OAuth redirect return too).
  client.auth.getSession().then(function (result) {
    var session = result.data && result.data.session;
    currentUser = session ? session.user : null;
    if (currentUser && window.AIFSProgress) {
      window.AIFSProgress.syncFromCloud(currentUser.id);
    }
    updateButton();
    notifyListeners();
  });

  // React to sign-in / sign-out / token refresh events.
  client.auth.onAuthStateChange(function (event, session) {
    var prevId = currentUser && currentUser.id;
    currentUser = session ? session.user : null;
    var nextId = currentUser && currentUser.id;

    if (event === 'SIGNED_IN' && window.AIFSProgress && currentUser) {
      window.AIFSProgress.syncFromCloud(currentUser.id);
    }
    if (event === 'SIGNED_OUT' && window.AIFSProgress) {
      window.AIFSProgress.clearCloudUser();
    }

    if (prevId !== nextId) {
      updateButton();
      notifyListeners();
    }
  });

  function signIn() {
    var redirectTo = window.location.origin + window.location.pathname;
    client.auth.signInWithOAuth({
      provider: 'github',
      options: { redirectTo: redirectTo }
    });
  }

  function signOut() {
    client.auth.signOut();
  }

  function updateButton() {
    var btn = document.getElementById('authToggle');
    var label = document.getElementById('authLabel');
    var avatar = document.getElementById('authAvatar');
    if (!btn || !label) return;

    if (currentUser) {
      var meta = currentUser.user_metadata || {};
      var name = meta.user_name || meta.login || meta.name || 'You';
      var avatarUrl = meta.avatar_url || '';
      if (avatar) {
        avatar.src = avatarUrl;
        avatar.style.display = avatarUrl ? 'inline-block' : 'none';
      }
      label.textContent = name;
      btn.title = 'Sign out';
      btn.setAttribute('data-signed-in', 'true');
    } else {
      if (avatar) avatar.style.display = 'none';
      label.textContent = 'Sign in';
      btn.title = 'Sign in with GitHub';
      btn.removeAttribute('data-signed-in');
    }
  }

  function initButton() {
    var btn = document.getElementById('authToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      if (currentUser) {
        signOut();
      } else {
        signIn();
      }
    });
    updateButton();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initButton);
  } else {
    initButton();
  }

  window.AIFSAuth = {
    signIn: signIn,
    signOut: signOut,
    getUser: function () { return currentUser; },
    getClient: function () { return client; },
    onChange: function (fn) { if (typeof fn === 'function') authListeners.push(fn); }
  };
})();
