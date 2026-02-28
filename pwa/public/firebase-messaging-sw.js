importScripts('https://www.gstatic.com/firebasejs/11.0.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/11.0.1/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: "AIzaSyAGJFSH02kBRahAuc6Zkwrdkq9PoBHtdVg",
  authDomain: "aerofinder-98cf7.firebaseapp.com",
  projectId: "aerofinder-98cf7",
  storageBucket: "aerofinder-98cf7.firebasestorage.app",
  messagingSenderId: "237067866769",
  appId: "1:237067866769:web:44f9555ff6cdcbacb36530"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/vite.svg', // Update icon path
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
