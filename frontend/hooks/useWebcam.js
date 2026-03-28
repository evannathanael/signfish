import { useCallback, useEffect, useRef, useState } from 'react';

export function useWebcam() {
  const videoRef = useRef(null);
  const [error, setError] = useState('');
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let active = true;
    let mediaStream;

    async function setup() {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (!active) return;
        if (videoRef.current) {
          const videoElement = videoRef.current;
          videoElement.srcObject = mediaStream;
          videoElement.onloadedmetadata = async () => {
            if (!active) return;
            try {
              await videoElement.play();
            } catch {
              // Browser may block autoplay until user interaction.
            }
            setIsReady(true);
          };
        }
      } catch {
        setError('Webcam permission denied or unavailable.');
      }
    }

    setup();

    return () => {
      active = false;
      setIsReady(false);
      mediaStream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    if (!video) return null;
    if (!isReady || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return null;
    if (!video.videoWidth || !video.videoHeight) return null;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.8);
  }, [isReady]);

  return { videoRef, captureFrame, error, isReady };
}
