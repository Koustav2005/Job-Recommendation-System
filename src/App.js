import React from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
// ...existing imports...

function App() {
  const isAuthenticated = () => {
    // Replace this with your actual authentication logic
    return !!localStorage.getItem('authToken');
  };

  return (
    <Router>
      <Switch>
        <Route path="/login" component={Login} />
        <Route path="/register" component={Register} />
        <Route
          path="/"
          render={() =>
            isAuthenticated() ? <Home /> : <Redirect to="/login" />
          }
        />
        {/* ...existing routes... */}
      </Switch>
    </Router>
  );
}

export default App;
