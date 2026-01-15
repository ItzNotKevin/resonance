import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { HomeScreen } from './src/screens/HomeScreen';
import { SwipeScreen } from './src/screens/SwipeScreen';
import { AccountScreen } from './src/screens/AccountScreen';
import { LikedSongsScreen } from './src/screens/LikedSongsScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  const { user } = useAuth();

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          cardStyle: { backgroundColor: '#f5f5f5' },
        }}
      >
        {!user ? (
          <Stack.Screen name="Home" component={HomeScreen} />
        ) : (
          <>
            <Stack.Screen name="Swipe" component={SwipeScreen} />
            <Stack.Screen 
              name="Account" 
              component={AccountScreen}
              options={{
                headerShown: true,
                title: 'Account',
                headerStyle: {
                  backgroundColor: 'white',
                },
                headerTintColor: '#1a1a1a',
                headerTitleStyle: {
                  fontWeight: '800',
                },
              }}
            />
            <Stack.Screen 
              name="LikedSongs" 
              component={LikedSongsScreen}
              options={{
                headerShown: false,
              }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppNavigator />
      <StatusBar style="auto" />
    </AuthProvider>
  );
}
