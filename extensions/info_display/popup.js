document.addEventListener('DOMContentLoaded', function() {
  // Display User Agent
  const userAgentElement = document.getElementById('user-agent');
  userAgentElement.textContent = navigator.userAgent;
  
  // Get and display IP address
  const ipAddressElement = document.getElementById('ip-address');
  const statusText = document.getElementById('status-text');
  
  fetch('https://api.ipify.org?format=json')
    .then(response => response.json())
    .then(data => {
      ipAddressElement.textContent = data.ip;
      statusText.textContent = 'Connected';
    })
    .catch(error => {
      ipAddressElement.textContent = 'Error fetching IP address';
      statusText.textContent = 'Connection error';
      document.querySelector('.status-icon').style.backgroundColor = '#ea4335';
      console.error('Error:', error);
    });
  
  // Display screen resolution
  const screenResolutionElement = document.getElementById('screen-resolution');
  screenResolutionElement.textContent = `${window.screen.width} x ${window.screen.height} (${window.devicePixelRatio}x ratio)`;
  
  // Display browser language
  const browserLanguageElement = document.getElementById('browser-language');
  browserLanguageElement.textContent = navigator.language || navigator.userLanguage;
  
  // Copy to clipboard functionality
  document.getElementById('copy-ua').addEventListener('click', function() {
    copyToClipboard(userAgentElement.textContent);
    this.textContent = 'Copied!';
    setTimeout(() => { this.textContent = 'Copy to clipboard'; }, 1500);
  });
  
  document.getElementById('copy-ip').addEventListener('click', function() {
    copyToClipboard(ipAddressElement.textContent);
    this.textContent = 'Copied!';
    setTimeout(() => { this.textContent = 'Copy to clipboard'; }, 1500);
  });
  
  function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }
});