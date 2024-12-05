export class Utils {
  private static instance: Utils | undefined;

  private constructor() {
  }

  public static getInstance(): Utils {
    // biome-ignore lint/complexity/noThisInStatic: <explanation>
    // biome-ignore lint/suspicious/noAssignInExpressions: <explanation>
        return this.instance || (this.instance = new Utils());
  }

  public onLoad(cb: () => void | Promise<void>): Promise<void> {
    return new Promise((resolve, reject) => {
      const runCallback = () => Promise.resolve().then(cb).then(resolve, reject);

      if (window.document.readyState === 'complete') {
        runCallback();
      } else {
        const listener = () => {
          window.removeEventListener('load', listener);
          runCallback();
        };

        window.addEventListener('load', listener);
      }
    });
  }

  public pascalToKebabCase(input: string): string {
    return input.
      replace(/^[A-Z]/, m => m.toLowerCase()).
      replace(/[A-Z]/g, m => `-${m.toLowerCase()}`);
  }

  public sleep(duration: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, duration));
  }

  public async waitAndCheck(interval: number, attempts: number, conditionFn: () => boolean): Promise<boolean> {
    while (!conditionFn()) {
      // biome-ignore lint/style/noParameterAssign: <explanation>
      if (--attempts < 0) return false;
      await this.sleep(interval);
    }

    return true;
  }
}
