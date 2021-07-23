% Setting x as symbolic variable
syms x;

% Input Section
p = input('Order of your equation: '); % the extra input I want for new algorithm
y = input('Enter non-linear equations: ');
e = input('Tolerable error: ');

% Finding Functional Value this part contains modification in bisection
% method
 a = -1*(eval(subs(y,x,0)))^(1/p)% Here we are asking for interval this is the method to 
 b = (eval(subs(y,x,0)))^(1/p)% Decide the interval Here interval is (a, b) and rest method is bisection only
fa = eval(subs(y,x,a))
fb = eval(subs(y,x,b));


% Implementing Bisection Method
if fa*fb > 0 
    disp('Given initial values do not bracket the root.');
else
    c = (a+b)/2;
    fc = eval(subs(y,x,c));
    fprintf('\n\na\t\t\tb\t\t\tc\t\t\tf(c)\n');
    while abs(fc)>e
        fprintf('%f\t%f\t%f\t%f\n',a,b,c,fc);
        if fa*fc< 0
            b =c;
        else
            a =c;
        end
        c = (a+b)/2;
        fc = eval(subs(y,x,c));
    end
    fprintf('\nRoot is: %f\n', c);
end