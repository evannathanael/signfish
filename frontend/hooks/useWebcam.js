import { useEffect, useRef, useState } from 'react';

export function useWebcam() {
  const videoRef = useRef(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    let mediaStream;

    async function setup() {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (!active) return;
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch {
        setError('Webcam permission denied or unavailable.');
      }
    }

    setup();

    return () => {
      active = false;
      mediaStream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  function captureFrame() {
    const video = videoRef.current;
    if (!video) return null;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.8);
  }

  return { videoRef, captureFrame, error };
}
