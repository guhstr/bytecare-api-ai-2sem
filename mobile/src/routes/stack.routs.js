import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { PrivateRoute } from "../components/PrivateRoute";

import Login from "../screens/Login";
import Signup from "../screens/Signup";
import Home from "../screens/Home";
import Animal from "../screens/Animal";
import Preventivo from "../screens/Preventivo";
import Terapeutico from "../screens/Terapeutico";
import BemEstar from "../screens/BemEstar";
import SubcategoriaListagem from "../screens/SubcategoriaListagem";
import Push from "../screens/Push";
import AnaliseIA from "../screens/AnaliseIA";
import ChatIA from "../screens/ChatIA";

const Stack = createNativeStackNavigator();

export default function Routes() {
  return (
    <Stack.Navigator
      initialRouteName="Login"
      screenOptions={{
        headerShown: false,
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="Login" component={Login} />
      <Stack.Screen name="Signup" component={Signup} />

      <Stack.Screen name="Home">
        {(props) => (
          <PrivateRoute {...props}>
            <Home {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="SubcategoriaListagem">
        {(props) => (
          <PrivateRoute {...props}>
            <SubcategoriaListagem {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="animal">
        {(props) => (
          <PrivateRoute {...props}>
            <Animal {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="Preventivo">
        {(props) => (
          <PrivateRoute {...props}>
            <Preventivo {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="Terapeutico">
        {(props) => (
          <PrivateRoute {...props}>
            <Terapeutico {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="BemEstar">
        {(props) => (
          <PrivateRoute {...props}>
            <BemEstar {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="AnaliseIA">
        {(props) => (
          <PrivateRoute {...props}>
            <AnaliseIA {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="ChatIA">
        {(props) => (
          <PrivateRoute {...props}>
            <ChatIA {...props} />
          </PrivateRoute>
        )}
      </Stack.Screen>

      <Stack.Screen name="Push" component={Push} />
    </Stack.Navigator>
  );
}
