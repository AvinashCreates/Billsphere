import {
  BrowserRouter,
  Routes,
  Route,
  useLocation
} from "react-router-dom";

import { useEffect } from "react";


import Navbar from "./components/Navbar";
import CommandPalette from "./components/CommandPalette";
import Footer from "./components/Footer";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";


import DashboardLayout from "./layouts/DashboardLayout";


import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Invoices from "./pages/Invoices";
import Plans from "./pages/Plans";
import Settings from "./pages/Settings";
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";





function AppContent(){


const location = useLocation();



useEffect(() => {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const shouldUseDark = savedTheme === "dark" || (!savedTheme && prefersDark);

  document.documentElement.classList.toggle("dark", shouldUseDark);
  document.documentElement.style.colorScheme = shouldUseDark ? "dark" : "light";
}, []);





const publicPages = [
  "/",
  "/login",
  "/register",
  "/forgot-password",
];

const showNavbar = publicPages.includes(location.pathname);






return(

<>


{
showNavbar && <Navbar/>
}

<CommandPalette />

<Routes>


{/* Public */}

<Route

path="/"

element={<Landing/>}

/>



<Route

path="/login"

element={<Login/>}

/>




<Route

path="/register"

element={<Register/>}

/>





{/* Dashboard */}

<Route element={<DashboardLayout/>}>


<Route

path="/dashboard"

element={<Dashboard/>}

/>



<Route

path="/customers"

element={<Customers/>}

/>



<Route

path="/invoices"

element={<Invoices/>}

/>



<Route

path="/plans"

element={<Plans/>}

/>



<Route

path="/settings"

element={<Settings/>}

/>



<Route

path="/profile"

element={<Profile/>}

/>


</Route>





<Route

path="/forgot-password"

element={<ForgotPassword/>}

/>



</Routes>

<Footer />

</>


)

}






function App(){
  return(

<BrowserRouter>

<AppContent/>

</BrowserRouter>

)

}



export default App;