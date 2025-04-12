// Content script that runs on all pages
// This script adds a floating info box that shows user agent and IP 

// Create the floating info display
function createInfoDisplay() {
  // Check if the display already exists
  if (document.getElementById('bsm-info-display')) {
    return;
  }
  
  // Create container
  const container = document.createElement('div');
  container.id = 'bsm-info-display';
  
  // Apply styles
  Object.assign(container.style, {
    position: 'fixed',
    bottom: '10px',
    right: '10px',
    backgroundColor: 'rgba(66, 133, 244, 0.9)',
    color: 'white',
    padding: '8px 12px',
    borderRadius: '4px',
    zIndex: '9999',
    fontSize: '12px',
    fontFamily: 'monospace',
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
    maxWidth: '300px',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    transition: 'opacity 0.3s, transform 0.3s',
    cursor: 'pointer'
  });
  
  // Create title bar with minimize button
  const titleBar = document.createElement('div');
  titleBar.style.display = 'flex';
  titleBar.style.justifyContent = 'space-between';
  titleBar.style.alignItems = 'center';
  titleBar.style.marginBottom = '5px';
  
  const title = document.createElement('div');
  title.textContent = '🔍 Browser Info';
  title.style.fontWeight = 'bold';
  
  const minimizeBtn = document.createElement('span');
  minimizeBtn.textContent = '_';
  minimizeBtn.style.cursor = 'pointer';
  minimizeBtn.style.marginLeft = '8px';
  minimizeBtn.onclick = (e) => {
    e.stopPropagation();
    toggleMinimized();
  };
  
  titleBar.appendChild(title);
  titleBar.appendChild(minimizeBtn);
  container.appendChild(titleBar);
  
  // Create info elements
  const userAgentInfo = document.createElement('div');
  userAgentInfo.id = 'bsm-user-agent';
  userAgentInfo.textContent = 'User-Agent: ' + navigator.userAgent;
  userAgentInfo.style.wordBreak = 'break-all';
  container.appendChild(userAgentInfo);
  
  const ipInfo = document.createElement('div');
  ipInfo.id = 'bsm-ip-address';
  ipInfo.textContent = 'IP: Loading...';
  container.appendChild(ipInfo);
  
  const languageInfo = document.createElement('div');
  languageInfo.id = 'bsm-language';
  languageInfo.textContent = 'Language: ' + (navigator.language || navigator.userLanguage);
  container.appendChild(languageInfo);
  
  const screenInfo = document.createElement('div');
  screenInfo.id = 'bsm-screen';
  screenInfo.textContent = 'Screen: ' + window.screen.width + 'x' + window.screen.height;
  container.appendChild(screenInfo);
  
  // Get and display WebGL info
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      if (debugInfo) {
        const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        
        const webglInfo = document.createElement('div');
        webglInfo.id = 'bsm-webgl';
        webglInfo.textContent = 'WebGL: ' + vendor + ' / ' + renderer;
        webglInfo.style.wordBreak = 'break-all';
        container.appendChild(webglInfo);
      }
    }
  } catch (e) {
    console.log('Could not get WebGL info:', e);
  }
  
  // Add to document
  document.body.appendChild(container);
  
  // Get IP address
  fetch('https://api.ipify.org?format=json')
    .then(response => response.json())
    .then(data => {
      ipInfo.textContent = 'IP: ' + data.ip;
    })
    .catch(error => {
      ipInfo.textContent = 'IP: Error fetching';
      console.error('Error fetching IP:', error);
    });
  
  // Add minimize/expand functionality
  let minimized = false;
  
  function toggleMinimized() {
    minimized = !minimized;
    if (minimized) {
      // Hide all info elements except the title
      userAgentInfo.style.display = 'none';
      ipInfo.style.display = 'none';
      if (languageInfo) languageInfo.style.display = 'none';
      if (screenInfo) screenInfo.style.display = 'none';
      const webglInfo = document.getElementById('bsm-webgl');
      if (webglInfo) webglInfo.style.display = 'none';
      
      minimizeBtn.textContent = '□';
      container.style.backgroundColor = 'rgba(66, 133, 244, 0.7)';
    } else {
      // Show all info elements
      userAgentInfo.style.display = 'block';
      ipInfo.style.display = 'block';
      if (languageInfo) languageInfo.style.display = 'block';
      if (screenInfo) screenInfo.style.display = 'block';
      const webglInfo = document.getElementById('bsm-webgl');
      if (webglInfo) webglInfo.style.display = 'block';
      
      minimizeBtn.textContent = '_';
      container.style.backgroundColor = 'rgba(66, 133, 244, 0.9)';
    }
  }
  
  // Toggle when clicking on the title
  titleBar.addEventListener('click', () => {
    toggleMinimized();
  });
  
  // Make draggable
  let isDragging = false;
  let dragOffsetX, dragOffsetY;
  
  titleBar.addEventListener('mousedown', function(e) {
    isDragging = true;
    dragOffsetX = e.clientX - container.getBoundingClientRect().left;
    dragOffsetY = e.clientY - container.getBoundingClientRect().top;
    e.preventDefault();
  });
  
  document.addEventListener('mousemove', function(e) {
    if (isDragging) {
      container.style.left = (e.clientX - dragOffsetX) + 'px';
      container.style.top = (e.clientY - dragOffsetY) + 'px';
      container.style.right = 'auto';
      container.style.bottom = 'auto';
    }
  });
  
  document.addEventListener('mouseup', function() {
    isDragging = false;
  });
}

// Initialize after page has loaded
window.addEventListener('load', function() {
  setTimeout(createInfoDisplay, 1000);
});