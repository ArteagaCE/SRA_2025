% SRA 2025 - Trabajo Practico de Laboratorio N4: Filtros Activos
% Aproximacion de Chebyshev y descomposicion en bicuadraticas (basado en el anexo de la guia)
clc; clear; close all;

%% Parametros de entrada
fp = [800 1250];   % Banda de paso [Hz]
fs = [200 5000];   % Banda de rechazo [Hz]
Wp = 2*pi*fp;      % [rad/s]
Ws = 2*pi*fs;      % [rad/s]
Ap = 0.25;         % Atenuacion maxima en banda de paso [dB]
As = 30;           % Atenuacion minima en banda de rechazo [dB]

%% Calculo de la funcion de transferencia
[n, Wn] = cheb1ord(Wp, Ws, Ap, As, 's');
[num, den] = cheby1(n, Ap, Wn, 's');
fprintf('T(s): num = '); fprintf('%.6g ', num); fprintf('\n');
fprintf('      den = '); fprintf('%.6g ', den); fprintf('\n');

[sos, g] = tf2sos(num, den);     % descomposicion en bicuadraticas

% Implementacion como pasabajos (seccion 1) y pasaaltos (seccion 2), como propone la guia
numPB = 2*g*sos(1,1:3); denPB = sos(1,4:6);
numPA = 1/2*sos(2,1:3); denPA = sos(2,4:6);
fprintf('PasaBajo: num = '); fprintf('%.6g ', numPB); fprintf(' den = '); fprintf('%.6g ', denPB); fprintf('\n');
fprintf('PasaAlto: num = '); fprintf('%.6g ', numPA); fprintf(' den = '); fprintf('%.6g ', denPA); fprintf('\n');

%% Parametros de cada bicuadratica
for k = 1:2
    wp = sqrt(sos(k,6)); Qp = wp/sos(k,5);
    fprintf('Seccion %d: fp = %.2f Hz, wp = %.2f rad/s, Qp = %.4f\n', k, wp/2/pi, wp, Qp);
end
fprintf('n = %d, g = %.6g\n', n, g);
fprintf('Atenuacion en 200 Hz: %.2f dB, en 5 kHz: %.2f dB\n', ...
    -20*log10(abs(freqs(num, den, 2*pi*[200 5000]))));
