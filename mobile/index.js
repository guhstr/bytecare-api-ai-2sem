import { registerRootComponent } from 'expo';
import { LogBox } from 'react-native';

LogBox.ignoreAllLogs(true);
console.warn = () => {};

import App from './App';

registerRootComponent(App);

