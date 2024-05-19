document.addEventListener('DOMContentLoaded', function() {
    const mediaElements = document.querySelectorAll('audio, video');
    
    if (mediaElements.length > 0) {
        alert('Media detected on this page. Press OK to download.');
        
        mediaElements.forEach(media => {
            const src = media.src;
            if (src) {
                const a = document.createElement('a');
                a.href = src;
                a.download = 'DownloadedMedia'; // This prompts the download, but naming might not be fully supported on iOS.
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
        });
    }
});
